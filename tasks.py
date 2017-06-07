# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import smtplib
import zipfile
import shutil

from cloud import s3_send
from email.mime.text import MIMEText
from parameterspace import celery
from createThumbs import create_thumbnails


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        shutil.copy(src, dest)


def del_files_in_dir(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def send_email_from_arup(recipient, email, project, pspace_url):
    """send email from within arup"""

    server = smtplib.SMTP('ausmtp01.arup.com')
    email_content = """<html>
                       <head></head>
                       <body>
                       <p>Gday {0},</p>
                       <p>Your ParamaterSpace for  project {1}
                       <a href="{3}">here!</a></p>
                       <p>Regards,</p>
                       <p>SpamBot</p>
                       </body>
                       </html><hr>{3}""".format(recipient, email, project, pspace_url)

    # Create a text/plain message
    msg = MIMEText(email_content.encode('ascii', 'replace'), 'html', 'ascii')
    msg['Subject'] = project
    msg['From'] = email
    msg['To'] = email
    # Send the message via our own SMTP server
    server.sendmail(email, email, msg.as_string())
    server.quit()


@celery.task(name='tasks.deploy')
def deploy_pspace(zip_location, owner, project, email):
    """task that will deply a site"""
    # unzip files
    zip_filepath, _ = os.path.splitext(zip_location)
    zip_ref = zipfile.ZipFile(zip_location, 'r')
    zip_ref.extractall(zip_filepath)
    zip_ref.close()

    # copy files from viewer to working_dir
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'viewer'))

    for item in os.listdir(root):
        copy(os.path.join(root, item), os.path.join(zip_filepath, item))

    # delete files in image directory
    del_files_in_dir(os.path.join(zip_filepath, 'images'))
    del_files_in_dir(os.path.join(zip_filepath, 'data'))

    # copy files into appropriate folders
    for item in os.listdir(zip_filepath):
        if item.lower().endswith('.png'):
            copy(os.path.join(zip_filepath, item),
                 os.path.join(zip_filepath, 'images', item))
        elif item.lower().endswith('.csv') or item.lower().endswith('.js'):
            copy(os.path.join(zip_filepath, item),
                 os.path.join(zip_filepath, 'data', item))

    # copy files into appropriate folders
    for item in os.listdir(zip_filepath):
        if item.lower().endswith('.png') or item.lower().endswith('.js') or item.lower().endswith('.csv'):
            os.remove(os.path.join(zip_filepath, item))

    # create thumbnails
    create_thumbnails(os.path.join(zip_filepath, 'images'), os.path.join(zip_filepath, 'images'))
    path_list = zip_filepath.split('\\')

    wdir = path_list.index('working_dir')
    path_list = path_list[wdir:]

    # _, url = s3_send('{0}.{1}'.format(directory, 'zip'), '{0}.{1}'.format(os.path.basename(directory), 'zip'))
    pspace_url = '{0}/{1}/{2}/{3}'.format('http://localhost:8888/parameterspace/', path_list[0], path_list[1], path_list[2])
    send_email_from_arup(owner, email, project, pspace_url)
