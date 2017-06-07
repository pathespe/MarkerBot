import io
import os
import sys
import subprocess
import importlib
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)
PYTHON_EXE = os.environ.get('PYTHON_EXE')


def check_answers(test_file, q_name, q_id):

    proc = subprocess.Popen(['C:\\Python27\\python.exe', '-u', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', test_file))], stdout=subprocess.PIPE)
    answers = [666, 42]
    results = []
    messages = []
    status  = 'Successful!'
    anss = []
    for i, line in enumerate(proc.stdout):
        ans = line.strip('\n')
        anss.append(ans)
        if ans == '':
            break
        else:
            if int(ans) == answers[i]:
                results.append(True)
                messages.append('<p>Nice one! Was expecting {0} and got {1}</p>'.format(answers[i], ans))
            else:
                results.append(False)
                messages.append('<p>Hmm not quite. Was expecting {0} but got {1}</p>'.format(answers[i], ans))
    if False in results:
        status = 'Unsuccessful'

    return {'q_id': q_id, 'question_name': q_name,'answers': anss, 'status': status,'results':results, 'messages':messages}


def call_functions_in_file(file_path, fname):

    MyClass = getattr(importlib.import_module('src.uploads.{0}'.format(file_path)), fname)
    instance = MyClass()
