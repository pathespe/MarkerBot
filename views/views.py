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
from tasks import check_function_task, check_console_task
from constants import CODE_KEY, PROFILE_KEY, EXTENTIONS

from markerbot import db

load_dotenv(os.path.join(os.path.dirname(__file__), '..',".env"))

AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
ALLOWED_EXTENSIONS = set(['txt', 'py'])
ROOT_URL = os.environ.get('ROOT_URL')

SESSIONS = [1, 2, 3, 4, 5, 6]

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
        r = requests.get('{1}/Session{0}/session_{0}_problems.md'.format(i, ROOT_URL), verify=False).text
        key = 'session_{0}'.format(i)
        json_dict[key] = markdown.markdown(r, extensions=EXTENTIONS)
    return json_dict

@index_view.route("/index")
@requires_auth
def index():
    course_readme = requests.get('{0}readme.md'.format(ROOT_URL), verify=False).text
    course_material_json = grab_latest_content()
    cheat_sheet = requests.get('{0}/cheat_sheet.md'.format(ROOT_URL)).text
    
    questions = []
    # there must be a better way to do this.. 
    for i in SESSIONS:
        questions.append(Question.query.filter(Question.session == i).all())
    
    return render_template('index.html',
                           user=session['profile'], 
                           questions=questions,
                           readme=course_readme,
                           cheatsheet=cheat_sheet,
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


@index_view.route("/mark-my-work", methods=['POST'])
def submit_file_for_marking():

    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"success":'No file'})

    recieved_file = request.files['file']

    # if user does not select file, browser also
    # submit a empty part without filename
    if recieved_file.filename == '':
        return jsonify({"success":'No selected file'})

    # if request makes sense
    if recieved_file and allowed_filetypes(recieved_file.filename):
        filename = secure_filename(recieved_file.filename)
        now = datetime.now()
        question_name = request.form['q_name']
        q_id = request.form['q_id']
        filename = os.path.join(os.getenv('UPLOAD_FOLDER'),
                                '%s.%s' % (now.strftime('p%Y_%m_%d_%H_%M_%S_%f'),
                                recieved_file.filename.rsplit('.', 1)[1]))
        recieved_file.save(filename)

        if q_id in ['q_id']:
            results = check_function_task.delay(filename, 'break_ur_markerbot', q_id)
        else:
            results = check_console_task.delay(filename, question_name, q_id)
        return jsonify(results)

    return 'wow how did you get here?'

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
    return redirect('/index')
