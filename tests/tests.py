from flask import json
import os
import sys
import unittest
import requests
from shutil import copyfile
from api import mark_work
# from dotenv import load_dotenv
# load_dotenv(os.path.join(os.path.dirname(__file__), '..',".env"))
# ROOT_URL = os.environ.get('ROOT_URL')
# p2app = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
# sys.path.append(p2app)

import application
db, app = application.run_setup()
from models.models import Result, User, Question
from marker.MarkExercise import check_functions
from views import views

def grab_questions(sessions, verify):
    """queries github pages for questions"""
    questions = []
    for sess_no in sessions:
        url = '{1}Session{0}/session_{0}_problems.json'.format(sess_no, 'https://raw.githubusercontent.com/ArupAus/lunchtimepython/2017/')
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

    def test_marker(self):

        filepath = os.path.join(os.path.dirname(__file__), 'resources', 'hello_world.py')
        copyfile(filepath, os.path.join("uploads",'hello_world.py'))
        result = check_functions(filepath, 'hello_world', [], ['hello world!'], 1)
        os.remove(os.path.join("uploads",'hello_world.py'))

        assert(result['result'])

        filepath = os.path.join(os.path.dirname(__file__), 'resources', 'example.py')
        copyfile(filepath, os.path.join("uploads",'example.py'))
        result = check_functions(filepath, 'hello_world', [], ['hello world!'], 1)
        os.remove(os.path.join("uploads",'example.py'))

        assert(result['result']==False)

    def tearDown(self):
        pass

class TestViews(unittest.TestCase):

    def setUp(self):
        pass

    def test_mocked_session(self):
         with app.test_client() as c:
            rv = c.get('api/user-progress/{0}/'.format(1))
            assert(rv.status_code == 200)

    def test_auth(self):
        with app.test_client() as c:
            rv = c.get('/index')
            assert(rv.status_code == 302)

    def test_splash(self):
        with app.test_client() as c:
            rv = c.get('/')
            assert(rv.status_code == 200)

    def test_logout(self):
        with app.test_client() as c:
            rv = c.get('/logout')
            assert(rv.status_code == 302)

    def test_aux_func(self):
        assert(views.allowed_filetypes('hkjlewf.py'))
        assert(views.allowed_filetypes('hkjlewf.svg')==False)
        
        json = views.grab_latest_content()
        assert(isinstance(json, dict))


    # def test_user_registration(self):
    #     with app.test_client() as c:
    #     #     with c.session_transaction() as sess:
    #     #         sess['profile'] = {'given_name': 'Lucy',
    #     #                            'family_name': 'Blanton', 
    #     #                            'nickname': 'Lucy.Blanton@arup.com'}

    #         assert(c.get('/callback')==200)

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
        with open(os.path.join(os.path.dirname(__file__),
                  'resources', 'users.csv')) as users_csv:
            for user in users_csv:
                split_parts = user.split(',')
                users.append(User(split_parts[0],
                                  split_parts[1],
                                  split_parts[2]))



        question_set = grab_questions([1, 2], True)
        db.session.add_all(question_set)
        db.session.commit()

        results = []
        with open(os.path.join(os.path.dirname(__file__),
                  'resources','results.csv')) as results_csv:
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

    def test_user_progress(self):
        with app.test_client() as client:
            rv = client.get('api/user-progress/1')
            assert(rv.status_code == 301)

    def test_rankings(self):
        with app.test_client() as client:
            rv = client.post('api/rankings')
            assert(rv.status_code == 405)
            rv = client.get('api/rankings')
            assert(rv.status_code == 200)

    def test_get_user_progress(self):
        result = mark_work.get_user_progress(1)
        assert(isinstance(result, list))
        assert(result[0]['correct']== False)
        fp = mark_work.print_divide_py3(os.path.join(os.path.dirname(__file__), 'resources','example.py'))
        assert(fp[1])
        with open(fp[0], 'r') as f_out:
            lines = f_out.readlines()
        assert(lines[0] == 'from __future__ import print_function\n')
        assert(lines[1] == 'from __future__ import division\n')

    def test_mark_work(self):
        with app.test_client() as client:
            rv = client.post('api/mark-my-work')
            assert(rv.status_code == 400)
            rv = client.get('api/mark-my-work')
            assert(rv.status_code == 405)


    def test_polling(self):
        with app.test_client() as client:
            rv = client.get('/marking-poll/<task_id>')
            
            assert(rv.status_code == 404)


    def tearDown(self):
        db.session.close()


if __name__ == '__main__':
    unittest.main()
