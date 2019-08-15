import sqlalchemy
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)

def connect(PoolConnection=False):
    '''Returns a connection and a metadata object'''
    url = os.environ['DATABASE_URL']
    if PoolConnection:
        con = sqlalchemy.create_engine(url, client_encoding='utf8')
    else:
        con = sqlalchemy.create_engine(url, client_encoding='utf8', poolclass=NullPool)

    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta
