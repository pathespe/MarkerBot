# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import smtplib
import zipfile
import shutil

from util.Cloud import s3_send
from email.mime.text import MIMEText
from markerbot import celery
from marker.MarkExercise import check_functions, check_console


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


def send_reminder_emailp(recipient, email, question, url):
    """send email from within arup"""

    server = smtplib.SMTP('ausmtp01.arup.com')
    email_content = """<html>
                       <head></head>
                       <body>
                       <p>Hey {0},</p>
                       <p>Learning to program takes time but what you put in now will save you time in the long run.
                       why not try your hand at {1}
                       <a href="{3}">here!</a></p>
                       <p>Regards,</p>
                       <p>Lunchtime Python Team</p>
                       </body>
                       </html><hr>{3}""".format(recipient, email, question, url)

    # Create a text/plain message
    msg = MIMEText(email_content.encode('ascii', 'replace'), 'html', 'ascii')
    msg['Subject'] = 'Its been a while...'
    msg['From'] = email
    msg['To'] = email
    # Send the message via our own SMTP server
    server.sendmail(email, email, msg.as_string())
    server.quit()


@celery.task(name='tasks.check_function_task')
def check_function_task(file_path, q_id):
    """task that will deply a site"""
    # query DB for question and get info required

    function_name = ''
    answers = 42

    return check_functions(file_path, function_name, answers)


@celery.task(name='tasks.check_console_task')
def check_console_task(test_file, q_id):
    """task that will run python in a separate process and parse stdout"""
    # query DB for question and get info required
    q_name = ''
    answers = 42
    return check_console(test_file, q_name, answers)


@celery.task(name='tasks.spam_users')
def spam_users(file_path, function_name, q_id, answers):
    # hassle users that have stopped logging in and completing questions...?
    # could check for last attempt in results table if its been over 
    # 2 weeks send them an email saying we miss you try this question
    # send_reminder_emailp(recipient, email, question, url)
    pass

@celery.task(name='tasks.clean_up')
def clean_up(file_path, function_name, q_id, answers):
    """task that will clean up uploads directory, run once a day?"""
    pass


@celery.task(name='tasks.check_question_set')
def check_question_set(file_path, function_name, q_id, answers):
    """task that will check for new questions"""
    pass