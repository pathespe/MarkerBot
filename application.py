import os
import logging
from logging.handlers import RotatingFileHandler
from sys import stdout

import psycopg2
from dotenv import load_dotenv
from werkzeug.local import LocalProxy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from celery import Celery
from flaskext.markdown import Markdown

import config

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(dotenv_path)


app = Flask(__name__, static_url_path='/static')
app.config.from_object(os.environ['APP_SETTINGS'])
formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = RotatingFileHandler(os.environ['LOG_FILENAME'], maxBytes=10000000, backupCount=5)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
app.logger.addHandler(handler)


def make_celery(app):
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


def run_setup():
    """ create app and register_blueprints"""
    from views.views import index_view
    from api.mark_work import mark_api

    extentions = ['markdown.extensions.extra',
                  'sane_lists', 'codehilite',
                  'admonition', 'meta',
                  'headerid', 'nl2br',
                  'smarty', 'toc',
                  'wikilinks']
    Markdown(app, extensions=extentions)
    app.register_blueprint(mark_api.blueprint, url_prefix='/api')
    app.register_blueprint(index_view)
    db.app = app
    db.init_app(app)
    return db, app


db = SQLAlchemy()
celery = make_celery(app)
CORS(app)
logger = LocalProxy(lambda: app.logger)


if __name__ == '__main__':
    db, app = run_setup()
    app.run('0.0.0.0')
