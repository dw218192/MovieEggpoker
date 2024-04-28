import os

from flask import Flask
import sqlite3
import random
import logging
import datetime
import uuid
from threading import Thread, Event
import atexit
from .consts import *

class UserSession:
    @staticmethod
    def is_valid(session) -> bool:
        return 'id' in session and 'last_active' in session

    def __init__(self, flask_session) -> None:
        if UserSession.is_valid(flask_session):
            self.id = flask_session['id']
            self.last_active = flask_session['last_active']
            self.flask_session = flask_session
            debug_log(f'retrieve session: {self.id}')
            return
        else:
            self.id = uuid.uuid4()
            self.last_active = datetime.datetime.now()
            self.flask_session = flask_session
            flask_session['id'] = self.id
            flask_session['last_active'] = self.last_active
            debug_log(f'new session: {self.id}')

    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, UserSession):
            return False
        return self.id == value.id

    def delete(self):
        self.flask_session.pop('id', None)
        self.flask_session.pop('last_active', None)
        debug_log(f'delete session {self.id}')

    def keep_alive(self):
        self.last_active = datetime.datetime.now()

    def is_inactive(self):
        return (datetime.datetime.now() - self.last_active).total_seconds() > 1200

def get_logger():
    return logging.getLogger(__name__)

def debug_log(message):
    get_logger().log(logging.DEBUG, message)

g_tick_funcs = []
# periodic cleanup of inactive threads
def tick_func(func):
    g_tick_funcs.append(func)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=random.randbytes(16) if not app.debug else 'dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # set up periodic tick
    app._shutdown_event = Event()
    def _tick():
        while not app._shutdown_event.is_set():
            for func in g_tick_funcs:
                func()
            app._shutdown_event.wait(TICK_INTERVAL)
    def _exit():
        app._shutdown_event.set()
        app._tick_thread.join()
    
    atexit.register(_exit)
    app._tick_thread = Thread(target=_tick)

    # ensure the local folder exists
    import os
    try:
        os.makedirs('_local')
    except FileExistsError:
        pass
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # set up logging
    get_logger().setLevel(app.debug)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    # clear log file
    if os.path.exists(LOG_FILE_PATH):
        open(LOG_FILE_PATH, 'w').close()
    get_logger().addHandler(file_handler)

    # register blueprints
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

    app._tick_thread.start()
    return app