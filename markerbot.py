from flask import Flask, flash, url_for, request, redirect, jsonify
from flask import render_template
import os
from datetime import datetime
from flaskext.markdown import Markdown
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import requests
import json
import markdown

from src.MarkExercise import check_answers
ALLOWED_EXTENSIONS = set(['txt', 'py'])

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(dotenv_path)
ROOT_URL = os.environ.get('ROOT_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # 2 mb files which should be plenty
app.secret_key = SECRET_KEY
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


questions = [
    [
    ('Rounding Numbers', 'qid_1'),
    ('Greetings', 'qid_2'),
    ('FizzBuzz', 'qid_3'),
    ('Double Char', 'qid_4'),
    ('Sum', 'qid_5')],
    [
    ('Strings', 'qid_6'),
    ('Print a Triangle', 'qid_7'),
    ('Prime Numbers', 'qid_8')],
    [
    ('Data Analysis', 'qid_9'),
    ('Square Check', 'qid_10'),
    ('Append Check', 'qid_11'),
    ('Into The Wild', 'qid_12')],
    [
    ('Evaluating Lines', 'qid_13'),
    ('Tails', 'qid_14'),
    ('Personable Greg', 'qid_15'),
    ('Chasing outstanding debts', 'qid_16')
    ]
]

def allowed_filetypes(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def grab_latest_content():
    json_dict = {}
    for i in range(1,5):
        r = requests.get('{1}/Session{0}/session_{0}_problems.md'.format(i, ROOT_URL)).text
        key = 'session_{0}'.format(i)
        json_dict[key] = markdown.markdown(r, extensions=extentions)
    return json_dict

@app.route("/")
def index():
    course_readme = requests.get('{0}readme.md'.format(ROOT_URL)).text
    course_material_json = grab_latest_content()
    return render_template('index.html',questions=questions, readme=course_readme, course_material=course_material_json)


@app.route("/mark-my-work", methods=['POST'])
def submit_file_for_marking():

    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"success":'No file'})

    file = request.files['file']

    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return jsonify({"success":'No selected file'})

    # if request makes sense
    if file and allowed_filetypes(file.filename):
        filename = secure_filename(file.filename)
        now = datetime.now()
        question_name = request.form['q_name']
        q_id = request.form['q_id']
        filename = os.path.join(app.config['UPLOAD_FOLDER'],
                                '%s.%s' % (now.strftime('p%Y_%m_%d_%H_%M_%S_%f'),
                                file.filename.rsplit('.', 1)[1]))
        file.save(filename)
        return jsonify(check_answers(filename, question_name, q_id))
    return 'wow how did you get here?'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run()