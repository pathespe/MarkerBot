import os
from logging import StreamHandler
from sys import stdout
import psycopg2
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from celery import Celery
from flaskext.markdown import Markdown
import urllib
import config

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(dotenv_path)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

app = Flask(__name__, static_url_path='/static')

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 
app.secret_key = os.getenv('SECRET_KEY')
app.config['CELERY_BACKEND'] = 'db+postgresql+psycopg2://{0}'.format(os.environ.get('DB'))
app.config['CELERY_BROKER_URL'] = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe=''),
                                                    urllib.quote(AWS_SECRET_ACCESS_KEY, safe=''))
app.config['BROKER_TRANSPORT_OPTIONS'] = {'region': AWS_REGION,
                                          'visibility_timeout': 43200,
                                          'polling_interval': 3}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


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
    extentions = ['markdown.extensions.extra',
                  'sane_lists', 'codehilite',
                  'admonition', 'meta',
                  'headerid', 'nl2br',
                  'smarty', 'toc',
                  'wikilinks']
    Markdown(app, extensions=extentions)

    app.register_blueprint(index_view)
    db.app = app
    db.init_app(app)
    handler = StreamHandler(stdout)
    app.logger.addHandler(handler)
    return db, app


db = SQLAlchemy()
celery = make_celery(app)
CORS(app)


if __name__ == '__main__':
    db, app = run_setup()
    app.run(host='0.0.0.0')
