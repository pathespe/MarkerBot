from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from parameterspace import db
import datetime


class Deployment(db.Model):
    """deployment model"""
    __tablename__ = 'deployments'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(), nullable=True)
    created_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    name = db.Column(db.String())
    client = db.Column(db.String())
    url = db.Column(db.String())

    def __init__(self, name, client, company, url):
        self.name = name
        self.client = client
        self.company = company
        self.url = url

    def __repr__(self):
        return '<deployment {0}, {1}>'.format(self.name, self.id)

class User(db.Model):
    """user model"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    surname = db.Column(db.String())
    email = db.Column(db.String())
    company = db.Column(db.String(), nullable=True)
    created_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, first_name, surname, email, company):
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.company = company

    def __repr__(self):
        return '<user {0}, {1}>'.format('{0}  {1} '.format(self.first_name, self.surname), self.id)

class Project(db.Model):
    """project model"""
    __tablename__ = 'projects'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    name = db.Column(db.String())
    owner = db.Column(db.Integer, ForeignKey(User.id))
    job_no = db.Column(db.String())

    def __init__(self, name, owner, job_no):
        self.name = name
        self.owner = owner
        self.job_no = job_no

    def __repr__(self):
        return '<project {0}, {1}>'.format(self.name, self.job_no)