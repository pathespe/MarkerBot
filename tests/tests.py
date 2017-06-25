from flask import json
import os
import sys
import unittest
import requests

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..',".env"))
ROOT_URL = os.environ.get('ROOT_URL')
p2app = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.append(p2app)

import application
db, app = application.run_setup()
from models.models import Result, User, Question

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

class TestMarker(unittest.TestCase):

    def setUp(self):
        pass

    def check_session1():
        pass

    def tearDown(self):
        pass

class TestApi(unittest.TestCase):

    def setUp(self):
        db.session.close()
        db.drop_all()
        db.create_all()
        self.populate_db()

    def populate_db(self):

        users = []
        with open(os.path.join(os.path.dirname(__file__), 'resources', 'users.csv')) as users_csv:
            for user in users_csv:
                split_parts = user.split(',')
                users.append(User(split_parts[0],
                                  split_parts[1],
                                  split_parts[2]))



        question_set = grab_questions([1, 2], True)
        db.session.add_all(question_set)
        db.session.commit()

        results = []
        with open(os.path.join(os.path.dirname(__file__), 'resources','results.csv')) as results_csv:
            for result in results_csv:
                split_parts = result.split(',')
                results.append(Result(int(split_parts[0]),
                                      int(split_parts[1]),
                                      bool(split_parts[2])))
        db.session.add_all(users)
        db.session.commit()
        db.session.add_all(results)
        db.session.commit()

    def test_db(self):
        query = db.session.query(User).all()
        assert(len(query) == 380)
        query = db.session.query(Result).all()
        assert(len(query) == 853)

    # def check_rankings():
    #     assert(create_JSON(answers, results, messages) == 200)

    def tearDown(self):
        db.session.close()



if __name__ == '__main__':
    unittest.main()
