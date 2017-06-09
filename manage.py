# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

import markerbot as mb
from markerbot import db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

_, app = mb.run_setup()

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint,
                                                        methods, rule))

        output.append(line)

    for line in sorted(output):
        print line


if __name__ == '__main__':
    manager.run()
