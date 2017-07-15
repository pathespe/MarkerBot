# -*- coding: utf-8 -*-
import os
import json
import logging

import requests
from dotenv import load_dotenv


dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','.env'))
load_dotenv(dotenv_path)


def send_function_failure(file_path, user_id, q_id, function_name, args, answers):
    message = '''```
                 File: {0}
                 User id: {1}
                 q_id: {2}
                 function_name: {3}
                 args: {4}
                 answers: {5}
                 ```
                 '''.format(file_path, user_id, q_id, function_name, args, answers)
    send_slack_message(message)


def send_slack_message(message):
    url = os.environ['SLACK_WEBHOOK']
    try:
        message_to_send = {'text': message}
        resp = requests.post(url, data=json.dumps(message_to_send))
    except Exception as e:
        logging.debug('Unable to send message to slack')
        logging.debug(e.message)

send_function_failure('jksjkf/kjhsdja/hello.py', 1, 23, 'greet', [213, 354, 54], [234, 556, 343])