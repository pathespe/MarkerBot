from flask import json
import os
import sys
import unittest

from src.MarkExercise import check_answers, create_JSON


questions = [
    [
    ('Rounding Numbers', 'qid_1'),
    ('Greetings', 'qid_2'),
    ('FizzBuzz', 'qid_3'),
    ('Double Char', 'qid_4'),
    ('Sum', 'qid_5')],
    [
    ('Strings', 'qid_6'),
    ('Print a Triangle', 'qid_7'),
    ('Prime Numbers', 'qid_8')],
    [
    ('Data Analysis', 'qid_9'),
    ('Square Check', 'qid_10'),
    ('Append Check', 'qid_11'),
    ('Into The Wild', 'qid_12')],
    [
    ('Evaluating Lines', 'qid_13'),
    ('Tails', 'qid_14'),
    ('Personable Greg', 'qid_15'),
    ('Chasing outstanding debts', 'qid_16')
    ]
]
function_questions = ['qid_1']


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
