import io
import os
import sys
import subprocess
import importlib
from dotenv import load_dotenv
from timeout import timeout

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)
PYTHON_EXE = os.environ.get('PYTHON_EXE')


def check_console(test_file, q_name, args, answers):

    proc = subprocess.Popen([PYTHON_EXE, '-u', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', test_file))], stdout=subprocess.PIPE)
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


def check_functions(file_path, function_name, args, answers, time_out):

    result = False
    try:
        filename = os.path.basename(file_path).split('.')[0]
        function = getattr(importlib.import_module('uploads.{0}'.format(filename)), function_name)
        func = timeout(timeout=time_out)(function)
        if len(args) == 0:
            ans = func()
        else:
            ans = func(*args)
        if [ans] == answers:
            result = True
        return {'input': args, 'result': result, 'output': ans, 'expected': answers}
    except Exception as e:
        return {'input': args, 'result': result, 'output': e.message, 'expected': answers}
