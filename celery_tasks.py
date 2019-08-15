# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import smtplib
import zipfile
import shutil
import pickle
import copy
import json

from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dotenv import load_dotenv
from celery.exceptions import SoftTimeLimitExceeded

from application import celery
from marker.MarkExercise import check_functions
from util.Cloud import s3_send
from util.sesEmail import Email
from util.DBUtilities import connect
from util.slack_notification import send_slack_message, send_function_failure
from models.models import Result
from application import logger

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '.env')))
ARUP_SMTP_SERVER = os.environ.get('ARUP_SMTP_SERVER')

NO_UNPACK = [20]
NESTED = [18, 19, 26, 27]
QUESTIONS_WTIH_FILES=[21, 22, 23, 24, 25, 26, 27, 28]

def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        shutil.copy(src, dest)


def del_files_in_dir(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def email_content(recipient, question, url):
    return """<html>
                <head></head>
                <body>
                  <p>Hey {0},</p>
                  <p>Learning to program takes time but what you put in now
                     will save you time in the long run.
                     why not try your hand at {1}
                  <a href="{3}">here!</a></p>
                  <p>Happy Coding,</p>
                  <p>Lunchtime Python Team</p>
                </body>
              </html>""".format(recipient, question, url)


def send_aws_email(recipient, email, question, url):
    """send email using SES, need to update so it can send to anyone"""
    content = email_content(recipient, question, url)
    email = Email(to=email, subject='Its been a while...')
    email.text(content)
    email.html(content)
    email.send()


def send_reminder_email(recipient, email, question, url):
    """send email from within arup"""
    server = smtplib.SMTP(ARUP_SMTP_SERVER)
    content = email_content(recipient, question, url)

    # Create a text/plain message
    msg = MIMEText(content.encode('ascii', 'replace'), 'html', 'ascii')
    msg['Subject'] = 'Its been a while...'
    msg['From'] = email
    msg['To'] = email
    # Send the message via our own SMTP server
    server.sendmail(email, email, msg.as_string())
    server.quit()



@celery.task(bind=True, name='celery_tasks.check_function_task', soft_time_limit=5, time_limit=10)
def check_function_task(self, file_path, user_id, q_id, function_name, args, answers, timeout):
    """task that will check a submission"""
    # this needs refactoring !
    results = []
    total = len(args)
    status = 'Unsucessful'
    sub_result = False

    try:
        for i, arg in enumerate(args):
            if q_id in QUESTIONS_WTIH_FILES:
                arg[0] = os.path.join('tests', 'resources', arg[0])
                if q_id in NESTED:
                    results.append(check_functions(file_path, function_name, arg, answers[i], timeout, nested=True))
                else:
                    results.append(check_functions(file_path, function_name, arg, answers[i], timeout, unbracket=True))

            elif q_id in NO_UNPACK:
                results.append(check_functions(file_path, function_name, arg, answers[i], timeout, no_unpack=True, unbracket=True))

            elif q_id in NESTED:
                results.append(check_functions(file_path, function_name, arg, answers[i], timeout, nested=True))

            else:
                results.append(check_functions(file_path, function_name, arg, answers[i], timeout, unbracket=True))

            self.update_state(state='PROGRESS', meta={'current': i, 'total': total, 'status': 'hold on m8!'})

        if all([x['result'] for x in results]):
            status = 'Successful!'
            sub_result = True

    except SoftTimeLimitExceeded:
        send_slack_message('SoftTimeLimitExceeded\n Submission Details:\n')
        send_function_failure(file_path, user_id, q_id, function_name, args, answers)
        logger.debug('Soft time exceeded')
        logger.debug(json.dumps({'question_name': function_name, 'current': i, 'q_id': q_id, 'total': total, 'status': status, 'result': results}))
        s3_send(file_path, os.path.basename(file_path))


    con, meta = connect()
    con.execute(meta.tables['results'].insert().values(user=int(user_id), question=q_id, submission_result=sub_result, created_date=datetime.now()))
    con.dispose()

    return {'question_name': function_name, 'current': i, 'q_id': q_id, 'total': total, 'status': status, 'result': results}


# @celery.task(name='celery_tasks.check_console_task')
# def check_console_task(test_file, q_id):
#     """task that will run python in a separate process and parse stdout"""
#     # query DB for question and get info required
#     q_name = ''
#     answers = 42
#     return check_console(test_file, q_name, answers)


# @celery.task(name='celery_tasks.spam_users')
# def spam_users(file_path, function_name, q_id, answers):
#     # hassle users that have stopped logging in and completing questions...?
#     # could check for last attempt in results table if its been over
#     # 2 weeks send them an email saying we miss you try this question
#     # send_reminder_emailp(recipient, email, question, url)
#     pass

# @celery.task(name='celery_tasks.clean_up')
# def clean_up(file_path, function_name, q_id, answers):
#     """task that will clean up uploads directory, run once a day?"""
#     pass


# @celery.task(name='celery_tasks.check_question_set')
# def check_question_set(file_path, function_name, q_id, answers):
#     """task that will check for new questions"""
#     pass
