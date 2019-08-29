from dotenv import load_dotenv
import os
import urllib
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(dotenv_path)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BACKEND = 'db+postgresql+psycopg2://{0}'.format(os.environ.get('DB'))
    BROKER_TRANSPORT_OPTIONS = {'region': AWS_REGION,
                                'visibility_timeout': 43200,
                                'polling_interval': 2,
                                'queue_name_prefix': 'markerbot'}
    CELERY_BROKER_URL = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe=''),
                                          urllib.quote(AWS_SECRET_ACCESS_KEY, safe=''))



class ProductionConfig(Config):
    DEBUG = False
    BROKER_TRANSPORT_OPTIONS = {'region': AWS_REGION,
                                'visibility_timeout': 43200,
                                'polling_interval': 2,
                                'queue_name_prefix': 'markerbot'}
    CELERY_BROKER_URL = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe=''),
                                          urllib.quote(AWS_SECRET_ACCESS_KEY, safe=''))

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    #CELERY_BROKER_URL = 'amqp://localhost//'
    BROKER_TRANSPORT_OPTIONS = {'region': AWS_REGION,
                                'visibility_timeout': 43200,
                                'polling_interval': 2,
                                'queue_name_prefix': 'markerbot'}
    CELERY_BROKER_URL = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe=''),
                                          urllib.quote(AWS_SECRET_ACCESS_KEY, safe=''))




class TestingConfig(Config):
    TESTING = True
    CSRF_ENABLED = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    CELERY_BROKER_URL = 'amqp://localhost//'
