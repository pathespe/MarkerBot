import io
import os
import sys
import subprocess
import importlib
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)
PYTHON_EXE = os.environ.get('PYTHON_EXE')


def check_answers(test_file, q_name):

    proc = subprocess.Popen(['C:\\Python27\\python.exe', '-u', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', test_file))], stdout=subprocess.PIPE)
    answers = ['3', 'str']
    results = []
    messages = []

    for i, line in enumerate(proc.stdout):
        ans = line.strip('\n')
        if ans == '':
            break
        else:
            if ans == answers[1]:
                results.append(True)
                messages.append('Nice one! Was expecting {0} and got {1}'.format(answers[i], ans))
            else:
                results.append(False)
                messages.append('Hmm not quite. Was expecting {0} but got {1}'.format(answers[i], ans))

    return {'answers': q_name, 'results':results, 'messages':messages}


def call_functions_in_file(file_path, fname):

    MyClass = getattr(importlib.import_module('src.uploads.{0}'.format(file_path)), fname)
    instance = MyClass()
