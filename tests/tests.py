from flask import json
import os
import sys
import unittest

from src.MarkExercise import check_answers, create_JSON

class TestApp(unittest.TestCase):

    def setUp(self):
        pass

    def check_session1():
        test_file = 'session_1.py'
        answers, results, messages = check_answers(test_file)
        assert(create_JSON(answers, results, messages) == 200)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
