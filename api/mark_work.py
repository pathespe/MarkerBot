# -*- coding: utf-8 -*-
"""api for marking code submissions"""
import os
import uuid
from flask import Blueprint, request, jsonify, url_for
from flask_restful import Api, Resource, reqparse
from celery_tasks import check_function_task
import werkzeug 
from application import db
from models.models import Question
from datetime import datetime


mark_api = Api(Blueprint('mark_api', __name__))


def mark_work_reqparse():
    """request parser for mark api"""
    lint_rp = reqparse.RequestParser()
    lint_rp.add_argument('q_name', type=str, required=True, help='No question provided', location='form')
    lint_rp.add_argument('q_id', type=str, required=True, help='No question id provided', location='form')
    lint_rp.add_argument('file', type=werkzeug.FileStorage, location='files')
    return lint_rp


@mark_api.resource("/mark-my-work")
class MarkWork(Resource):
    """mark work class"""

    @staticmethod
    def post():
        """
        submits work to queue work and sends client
        back a task id which can be polled for progress
        """
        parse = mark_work_reqparse()
        args = parse.parse_args()
        recieved_file = args['file']
        mimetype = recieved_file.content_type
        filename = werkzeug.secure_filename(recieved_file.filename)

        now = datetime.now()
        question_name = args['q_name']
        q_id = args['q_id']

        filename = os.path.join(os.getenv('UPLOAD_FOLDER'),
                                '%s.%s' % (now.strftime('p%Y_%m_%d_%H_%M_%S_%f'),
                                recieved_file.filename.rsplit('.', 1)[1]))

        recieved_file.save(filename)
        question = db.session.query(Question).filter_by(id=q_id).first()
        task = check_function_task.apply_async(args=[filename,
                                                     question.id,
                                                     question.function_name,
                                                     question.args,
                                                     question.answer,
                                                     question.timeout])

        return {'Location': url_for('mark_api.markpollapi', task_id=task.id)}


@mark_api.resource('/marking-poll/<task_id>')
class MarkPollAPI(Resource):
    """allow client to poll progress of marking process"""
    @staticmethod
    def get(task_id):
        task = check_function_task.AsyncResult(task_id)
        if task.state == 'PENDING':
            #job did not start yet
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
            if 'result' in task.info:
                response['result'] = task.info['result']
                response['question_name'] = task.info['question_name']
                response['total'] = task.info['total']
                response['q_id'] = task.info['q_id']
        else:
            # something went wrong in the background job
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info),  # this is the exception raised
            }
        return jsonify(response)
