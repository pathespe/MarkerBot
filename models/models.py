from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON
import datetime
from markerbot import db


class Question(db.Model):
    """deployment model"""
    __tablename__ = 'questions'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    question = db.Column(db.String())
    answer = db.Column(db.String())
    timeout = db.Column(db.Float())

    def __init__(self, name, question, answer, timeout):
        self.name = name
        self.question = question
        self.answer = answer
        self.timeout = timeout

    def __repr__(self):
        return '<question {0}, {1}>'.format(self.name, self.id)

class User(db.Model):
    """user model"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    surname = db.Column(db.String())
    email = db.Column(db.String())
    created_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, first_name, surname, email):
        self.first_name = first_name
        self.surname = surname
        self.email = email

    def __repr__(self):
        return '<user {0}, {1}>'.format('{0}  {1} '.format(self.first_name, self.surname), self.id)

class Result(db.Model):
    """project model"""

    __tablename__ = 'results'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    user = db.Column(db.Integer, ForeignKey(User.id))
    question = db.Column(db.Integer, ForeignKey(Question.id))
    submission_result = db.Column(db.Boolean)

    def __init__(self, owner, question, submission_result):
        self.owner = owner
        self.question = question
        self.submission_result = submission_result

    def __repr__(self):
        return '<Result {0}, {1}, {2}>'.format(self.name, self.question, self.submission_result)