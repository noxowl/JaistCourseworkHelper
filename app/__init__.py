import os.path

import yaml
from quart import Quart
from pathlib import Path

quart_app = Quart(__name__)
try:
    with Path(Path(os.path.dirname(__file__)).parent, 'config.yml').open('r') as conf:
        config = yaml.load(conf, Loader=yaml.FullLoader)
    quart_app.config.update(config)
    if quart_app.config['DATABASE_ENGINE'] == 'sqlite':
        quart_app.config.update({'DATABASE_PATH': os.path.join(Path(os.path.dirname(__file__)).parent,
                                                               'jaist_coursework_helper.db')
                           })
    quart_app.secret_key = quart_app.config['SECRET_KEY']
except Exception as e:
    print(e)

from app.db import initialize_db
from app.syllabus import Syllabus
from app import api
from app import routes

initialize_db()
setattr(quart_app, 'syllabus', Syllabus())
