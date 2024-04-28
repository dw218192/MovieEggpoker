import os

from flask import Flask
import sqlite3
import random
import logging

LOG_FILE_PATH = '_local/log.log'

def get_logger():
    return logging.getLogger(__name__)

def debug_log(message):
    get_logger().log(logging.DEBUG, message)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=random.randbytes(16) if not app.debug else 'dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    import os
    try:
        os.makedirs('_local')
    except FileExistsError:
        pass

    get_logger().setLevel(app.debug)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    # clear log file
    if os.path.exists(LOG_FILE_PATH):
        open(LOG_FILE_PATH, 'w').close()
    get_logger().addHandler(file_handler)

    from . import video_search, stream, manage
    app.register_blueprint(video_search.bp)
    app.register_blueprint(stream.bp)
    app.register_blueprint(manage.bp)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app