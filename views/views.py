from flask import request, render_template, redirect, session, Blueprint, jsonify
from functools import wraps
import requests
import os
import constants
from os import environ as env
from urlparse import urlparse
from models.models import Question, User, Result
from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Users
from datetime import datetime
from flaskext.markdown import Markdown
from functools import wraps
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json
import markdown
from marker.MarkExercise import check_console, check_functions
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), '..',".env"))

AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID =  os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET =  os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
CODE_KEY = os.getenv('CODE_KEY')
PROFILE_KEY = os.getenv('PROFILE_KEY')
ALLOWED_EXTENSIONS = set(['txt', 'py'])
ROOT_URL = os.environ.get('ROOT_URL')


extentions = ['markdown.extensions.extra',
              'markdown.extensions.toc',
              'sane_lists',
              'codehilite',
              'admonition',
              'meta',
              'headerid',
              'nl2br',
              'smarty',
              'toc',
              'wikilinks']


questions = [[
    ('Rounding Numbers', 'qid_1'),
    ('Greetings', 'qid_2'),
    ('FizzBuzz', 'qid_3'),
    ('Double Char', 'qid_4'),
    ('Sum', 'qid_5')], [
    ('Strings', 'qid_6'),
    ('Print a Triangle', 'qid_7'),
    ('Prime Numbers', 'qid_8')], [
    ('Data Analysis', 'qid_9'),
    ('Square Check', 'qid_10'),
    ('Append Check', 'qid_11'),
    ('Into The Wild', 'qid_12')], [
    ('Evaluating Lines', 'qid_13'),
    ('Tails', 'qid_14'),
    ('Personable Greg', 'qid_15'),
    ('Chasing outstanding debts', 'qid_16')
    ]
]
function_questions = ['qid_1']


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
    for i in range(1,5):
        r = requests.get('{1}/Session{0}/session_{0}_problems.md'.format(i, ROOT_URL), verify=False).text
        key = 'session_{0}'.format(i)
        json_dict[key] = markdown.markdown(r, extensions=extentions)
    return json_dict

@index_view.route("/index")
@requires_auth
def index():
    course_readme = requests.get('{0}readme.md'.format(ROOT_URL), verify=False).text
    course_material_json = grab_latest_content()
    return render_template('index.html',questions=questions, readme=course_readme, course_material=course_material_json)


@index_view.route('/logout')
@requires_auth
def logout():
    session.clear()
    parsed_base_url = urlparse(AUTH0_CALLBACK_URL)
    base_url = parsed_base_url.scheme + '://' + parsed_base_url.netloc
    return redirect('https://%s/v2/logout?returnTo=%s&client_id=%s' % (AUTH0_DOMAIN, base_url, AUTH0_CLIENT_ID))


@index_view.route('/')
def splash():
    env = {
        'AUTH0_CLIENT_ID': AUTH0_CLIENT_ID,
        'AUTH0_DOMAIN': AUTH0_DOMAIN,
        'AUTH0_CALLBACK_URL': AUTH0_CALLBACK_URL
    }
    # rq = random.choice(constants.QUOTES)
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

        if q_id in function_questions:
            results = check_functions(filename, 'break_ur_markerbot', q_id)
        else:
            results = check_console(filename, question_name, q_id)
        return jsonify(results)

    return 'wow how did you get here?'

@index_view.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@index_view.route('/callback')
def callback_handling():

    code = request.args.get(constants.CODE_KEY)
    get_token = GetToken(AUTH0_DOMAIN)
    auth0_users = Users(AUTH0_DOMAIN)
    token = get_token.authorization_code(AUTH0_CLIENT_ID,
                                         AUTH0_CLIENT_SECRET, code, AUTH0_CALLBACK_URL)
    user_info = auth0_users.userinfo(token['access_token'])
    session[constants.PROFILE_KEY] = json.loads(user_info)
    return redirect('/index')


    # trying to keep a reference in the session to who the user is
    # not sure if the way ive done it below is a good idea..
    # user_info = requests.get(u_url).json()
    # session[constants.PROFILE_KEY] = user_info

    # first_name = user_info['given_name']
    # surname = user_info['family_name']
    # email = user_info['email']
    # try:
    #     company = ''.join(email.split('@')[1].split('.')[:-1])
    # except:
    #     company = 'Not Implemented'

    # from models.models import User
    # from wind_whisperer import db
    # user = db.session.query(User).filter_by(first_name=first_name,
    #                                                surname=surname,
    #                                                email=email).first()

    # if(user is None):
    #     user = User(first_name=first_name,
    #                        surname=surname,
    #                        email=email,
    #                        company=company)
    #     db.session.add(user)
    #     db.session.commit()
    # session['user_id'] = user.id