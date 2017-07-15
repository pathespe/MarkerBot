import os
from functools import wraps
from urlparse import urlparse
from datetime import datetime
from flask import request, render_template, redirect, session, Blueprint, jsonify

from werkzeug.utils import secure_filename
from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Users
from dotenv import load_dotenv
import requests
import json
import markdown
from email.utils import parseaddr

from models.models import Question, User, Result
from celery_tasks import check_function_task
from constants import CODE_KEY, PROFILE_KEY, EXTENTIONS

from application import db

load_dotenv(os.path.join(os.path.dirname(__file__), '..',".env"))

AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
ALLOWED_EXTENSIONS = set(['txt', 'py'])
ROOT_URL = os.environ.get('ROOT_URL')

SESSIONS = [0, 1, 2, 3, 4, 5, 6] # hmmmmmm dunno about this

index_view = Blueprint('index', __name__)

# Requires authentication decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
          # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)

    return decorated

def allowed_filetypes(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def grab_latest_content():
    json_dict = {}
    for i in SESSIONS:
        r = requests.get('{1}/Session{0}/session_{0}_problems.md'.format(i, ROOT_URL)).text
        key = 'session_{0}'.format(i)
        json_dict[key] = markdown.markdown(r, extensions=EXTENTIONS)
    return json_dict

@index_view.route("/index")
@requires_auth
def index():
    pre_work = requests.get('https://raw.githubusercontent.com/ArupAus/lunchtimepython/2017/Session0/README.md').text
    course_readme = requests.get('{0}readme.md'.format(ROOT_URL)).text
    course_material_json = grab_latest_content()
    cheat_sheet = requests.get('{0}cheat_sheet.md'.format(ROOT_URL)).text

    questions = []
    # there must be a better way to do this.. 
    for i in SESSIONS:
        questions.append(Question.query.filter(Question.session == i).all())

    return render_template('index.html',
                           user=session['profile'],
                           user_id = session['user_id'],
                           questions=questions,
                           readme=course_readme,
                           pre_work = {'pre_work': markdown.markdown(pre_work, extensions=EXTENTIONS)},
                           cheatsheet={'cheat': markdown.markdown(cheat_sheet, extensions=EXTENTIONS)},
                           course_material=course_material_json)


@index_view.route('/logout')
@requires_auth
def logout():
    session.clear()
    parsed_base_url = urlparse(AUTH0_CALLBACK_URL)
    base_url = parsed_base_url.scheme + '://' + parsed_base_url.netloc
    return redirect('https://%s/v2/logout?returnTo=%s&client_id=%s' % (AUTH0_DOMAIN, base_url, AUTH0_CLIENT_ID))


@index_view.route('/')
def splash():
    """splash page when people arent logged in"""
    env = {
        'AUTH0_CLIENT_ID': AUTH0_CLIENT_ID,
        'AUTH0_DOMAIN': AUTH0_DOMAIN,
        'AUTH0_CALLBACK_URL': AUTH0_CALLBACK_URL
    }
    return render_template('splash.html', env=env)


@index_view.errorhandler(404)
def page_not_found(e):
    # log exception
    return render_template('404.html'), 404


@index_view.route('/callback')
def callback_handling():

    code = request.args.get(CODE_KEY)
    get_token = GetToken(AUTH0_DOMAIN)
    auth0_users = Users(AUTH0_DOMAIN)
    token = get_token.authorization_code(AUTH0_CLIENT_ID,
                                         AUTH0_CLIENT_SECRET, code, AUTH0_CALLBACK_URL)
    user_info = auth0_users.userinfo(token['access_token'])
    session[PROFILE_KEY] = json.loads(user_info)
    # return user_info
    # extract data to register user on DB in order top track question set progress
    register_user()

    return redirect('/index')

def register_user():
    first_name = session['profile']['given_name']
    surname = session['profile']['family_name']
    try:
        email = session['profile']['email']
    except Exception as e:
        # log exception arup waad has email in nickname for some reason...

        email = session['profile']['nickname']
        if len(parseaddr(email)[1]) == 0:
            return 'unable to log you in, invalid email supplied'

    user = db.session.query(User).filter_by(first_name=first_name,
                                            surname=surname,
                                            email=email).first()

    # if user doesnt exist in db, add them
    if(user is None):
        user = User(first_name=first_name,
                    surname=surname,
                    email=email)
        db.session.add(user)
        db.session.commit()

    # add user id from DB to the session
    session['user_id'] = user.id
    return True