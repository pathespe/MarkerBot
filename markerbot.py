import os
from logging import StreamHandler
from sys import stdout

import psycopg2
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_celery import make_celery
import config
from flaskext.markdown import Markdown
from views.views import index_view

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # 2 mb files which should be plenty
app.secret_key = os.getenv('SECRET_KEY')
app.config['CELERY_BACKEND'] = 'db+postgresql+psycopg2://localhost/markerbot'
app.config['CELERY_BROKER_URL'] = 'amqp://localhost//'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
celery = make_celery(app)
CORS(app)


def run_setup():
    """ create app and register_blueprints"""
    extentions = ['markdown.extensions.extra',
                  'sane_lists',
                  'codehilite',
                  'admonition',
                  'meta',
                  'headerid',
                  'nl2br',
                  'smarty',
                  'toc',
                  'wikilinks']
    Markdown(app, extensions=extentions)

    app.register_blueprint(index_view)
    db.app = app
    db.init_app(app)
    handler = StreamHandler(stdout)
    app.logger.addHandler(handler)
    return db, app


if __name__ == '__main__':
    db, app = run_setup()
    app.run(host='127.0.0.1', port=5000)
