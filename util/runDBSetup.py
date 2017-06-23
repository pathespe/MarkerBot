"""
script that will grab the latest question set and populate DB
you may want delete all rows in DB before hand to avoid collisions
"""


import os
import sys
import json
import requests
from dotenv import load_dotenv
from sqlalchemy import func
load_dotenv(os.path.join(os.path.dirname(__file__), '..',".env"))

ROOT_URL = os.environ.get('ROOT_URL')
p2app = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.append(p2app)

import application
from models.models import Question, User, Result



db, app = application.run_setup()
app.config.from_object(os.environ['APP_SETTINGS'])

def grab_questions(sessions, verify):
    """queries github pages for questions"""
    questions = []
    for sess_no in sessions:
        url = '{1}Session{0}/session_{0}_problems.json'.format(sess_no, ROOT_URL)
        resp = requests.get(url, verify=verify).text
        resp = json.loads(resp)
        for question in resp:
            questions.append(Question(name=question['name'],
                                      question=question['question'],
                                      function_name=question['function_name'],
                                      answer=question['answers'],
                                      args = question['args'],
                                      timeout=question['timeout'],
                                      session=sess_no))
    return questions

# question_set = grab_questions([1, 2], True)
# db.session.add_all(question_set)
# Result.query.filter(Result.user == user_id,
# a = Result.query.filter(Result.submission_result == True).count()
# q = db.session.query(Question).filter_by(id=1).first()






a = db.session.query(Result).filter(Result.submission_result == True).distinct(Result.user).all().count()

print a
# out = {}
# for result in a:
#     if result.User.first_name not in out.keys():
#         out[result.User.first_name] = 1
#     else:
#         out[result.User.first_name] += 1

# print out

db.session.commit()
db.session.close()
