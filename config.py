from dotenv import load_dotenv
import os

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class TestingConfig(Config):
    TESTING = True
    CSRF_ENABLED = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
