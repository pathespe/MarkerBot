# -*- coding: utf-8 -*-
"""api for marking code submissions"""
import os
import uuid
from flask import Blueprint, request, jsonify, url_for
from flask_restful import Api, Resource, reqparse
from celery_tasks import check_function_task
import werkzeug
from application import db
from models.models import Question, Result, User
from datetime import datetime
from collections import OrderedDict

mark_api = Api(Blueprint('mark_api', __name__))


def mark_work_reqparse():
    """request parser for mark api"""
    lint_rp = reqparse.RequestParser()
    lint_rp.add_argument('q_name', type=str, required=True, help='No question provided', location='form')
    lint_rp.add_argument('q_id', type=str, required=True, help='No question id provided', location='form')
    lint_rp.add_argument('user_id', type=int, required=True, help='No user id provided', location='form')
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
        user_id = int(args['user_id'])

        # return user_id
        filename = os.path.join(os.getenv('UPLOAD_FOLDER'),
                                '%s.%s' % (now.strftime('p%Y_%m_%d_%H_%M_%S_%f'),
                                recieved_file.filename.rsplit('.', 1)[1]))

        recieved_file.save(filename)
        print_divide_py3(filename)
        question = db.session.query(Question).filter_by(id=q_id).first()
        task = check_function_task.apply_async(args=[filename,
                                                     user_id,
                                                     question.id,
                                                     question.function_name,
                                                     question.args,
                                                     question.answer,
                                                     question.timeout])

        return {'Location': url_for('mark_api.markpollapi', task_id=task.id)}


def print_divide_py3(filepath):
    lines =[]
    with open(filepath, 'r') as f_in:
        lines = f_in.readlines()

    with open(filepath, 'w') as f_out:
        f_out.write('from __future__ import print_function\n')
        f_out.write('from __future__ import division\n\n')
        for line in lines:
            f_out.write(line)

    return filepath, True

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



def get_user_progress(user_id):

    user_progress = []
    questions = Question.query.all()

    for question in questions:
        query_result = Result.query.filter(Result.user == user_id,
                                           Result.question == question.id).all()
        attempts = len(query_result)
        q_result = False
        for qr in query_result:
            if qr.submission_result == True:
                q_result = True

        user_progress.append({
            'q_id': question.id,
            'q_name': question.name,
            'attempts': attempts,
            'correct': q_result
        })

    return user_progress

@mark_api.resource('/user-progress/<user_id>/')
class UserProgressAPI(Resource):
    """allow client to view rankings"""
    @staticmethod
    def get(user_id):
        return jsonify(get_user_progress(int(user_id)))

@mark_api.resource('/rankings')
class MarkRankingsAPI(Resource):
    """allow client to view rankings, absolute mess atm"""
    @staticmethod
    def get():

        # this needs to be refactored
        a = db.session.query(Result, User).filter(Result.user == User.id)\
            .filter(Result.submission_result == True).all()

        out = {}
        for result in a:
            if result.User.id not in out.keys():
                out[result.User.id] = {'user': '{0} {1}'.format(result.User.first_name, result.User.surname),
                                       'count': 1,
                                       'q_id': [result.Result.question] }
                continue
            if result.Result.question not in out[result.User.id]['q_id']:
                out[result.User.id]['count'] += 1
                out[result.User.id]['q_id'].append(result.Result.question)

        ordered = list(sorted(out.items(), key=lambda i: (i[1]['count'], i[1]['user']), reverse=True))

        return jsonify(ordered)
