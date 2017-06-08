""" Constants file for Auth0's seed project
"""
import os

ACCESS_TOKEN_KEY = 'access_token'
APP_JSON_KEY = 'application/json'
AUTH0_CLIENT_ID = 'O20Y34rc7q5Q46UuGeHOeNaWo8P2hsws'
AUTH0_CLIENT_SECRET = 'VncgF79UTJ9cYg4Ax8DEuzWbDpJGxcxLNAYWZW1hdLDi8HtkrZR_cqX_zYw-Givs'
AUTH0_CALLBACK_URL = 'http://127.0.0.1:5000/callback' #replace when in production
AUTH0_DOMAIN = 'arupdigital.au.auth0.com'
AUTHORIZATION_CODE_KEY = 'authorization_code'
CLIENT_ID_KEY = 'client_id'
CLIENT_SECRET_KEY = 'client_secret'
CODE_KEY = 'code'
CONTENT_TYPE_KEY = 'content-type'
GRANT_TYPE_KEY = 'grant_type'
PROFILE_KEY = 'profile'
REDIRECT_URI_KEY = 'redirect_uri'
SECRET_KEY = os.urandom(24)
LOGOUT_URL = 'http%3A%2F%2F127.0.0.1:5000/logout' #replace when in production
