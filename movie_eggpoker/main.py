from flask import Blueprint, render_template, request, jsonify, current_app, session, app, g

from . import get_logger, debug_log
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from youtubesearchpython import VideosSearch
from typing import Optional
from threading import Thread, Event
import queue
import uuid

bp = Blueprint('main', __name__)

user_sessions : dict[uuid.UUID, 'SearchThread'] = {}

@dataclass
class SearchResultItem:
    title: str
    url: str
    thumbnail: str
    width : int
    height : int

class SearchThread(Thread):
    CMD_NEXT_PAGE = 0
    CMD_PREV_PAGE = 1
    CMD_SEARCH = 2
    CMD_STOP = 3
    
    def __init__(self):
        super().__init__()
        self.msg_queue = queue.Queue()
        self.search_query = None

        # pages of search results
        self.cur_page = 0
        self.search_result : list[list[SearchResultItem]] = []
        self.search_engine : Optional[VideosSearch] = None

    def _handle_res(self, res: dict) -> list[SearchResultItem]:
        search_result = []
        for video in res['result']:
            width,height = 1080,720
            if len(video['thumbnails']) > 0:
                url = video['thumbnails'][0]['url']
            else:
                url = 'https://via.placeholder.com/640x480.png?text=No+thumbnail+found'                

            search_result.append(SearchResultItem(
                title = video['title'],
                url = video['link'],
                thumbnail = url,
                width = width,
                height = height
            ))
        return search_result

    def run(self):
        while True:
            # get a message from the queue
            cmd, msg, event = self.msg_queue.get()
            if cmd == self.CMD_STOP:
                event.set()
                break
            elif cmd == self.CMD_SEARCH:
                self.search_engine = VideosSearch(msg, limit = 10)
                self.cur_page = 0
                self.search_result = [self._handle_res(self.search_engine.result())]
                event.set()
            elif cmd == self.CMD_NEXT_PAGE:
                if not self.search_engine:
                    debug_log('search_engine is None')
                else:
                    if self.cur_page + 1 < len(self.search_result):
                        # use previously fetched results
                        self.cur_page += 1
                    else:
                        if self.search_engine.next():
                            self.cur_page += 1
                            self.search_result.append(self._handle_res(self.search_engine.result()))
                        else:
                            debug_log('No more search results')
                event.set()
            elif cmd == self.CMD_PREV_PAGE:
                if not self.search_engine:
                    debug_log('search_engine is None')
                else:
                    if self.cur_page > 0:
                        self.cur_page -= 1
                    else:
                        debug_log('No more search results')
                event.set()
            else:
                debug_log('Unknown command:', cmd)

    def get_search_result(self):        
        return self.search_result[self.cur_page]

    def send_msg(self, cmd, msg, event : Event):
        self.msg_queue.put((cmd, msg, event))

@bp.route('/search_video', methods=['GET'])
def search_video_v2():
    search_query = request.args.get('searchInput')
 
    if 'id' not in session or session['id'] not in user_sessions or not session['id']:
        id = uuid.uuid4()
        session['id'] = id
        debug_log(f'new session: {id}, active threads: {len(user_sessions)}')
        t = SearchThread()
        user_sessions[id] = t
        t.start()
    else:
        id = session['id']
        t = user_sessions[id]

    event = Event()
    t.send_msg(SearchThread.CMD_SEARCH, search_query, event)

    if not event.wait(20):
        return jsonify({'status': 'error', 'message': 'Search timeout'})
    return jsonify({'status': 'ok', 'search_result': t.get_search_result()})

@bp.route('/user_disconnected', methods=['GET'])
def user_disconnected():
    if 'id' in session:
        event = Event()
        id = session['id']
        session.pop('id', None)
        debug_log(f'user_disconnected: {id}, active threads: {len(user_sessions)}')
        if id in user_sessions:
            t = user_sessions[id]
            t.send_msg(SearchThread.CMD_STOP, None, event)
            del user_sessions[id]
    return jsonify({'status': 'ok'})

@bp.route('/next_page', methods=['GET'])
def next_page():
    if 'id' in session:
        id = session['id']
        debug_log(f'next_page: {id}')
        t = user_sessions[id]
        event = Event()
        t.send_msg(SearchThread.CMD_NEXT_PAGE, None, event)
        if not event.wait(20):
            return jsonify({'status': 'error', 'message': 'Next page timeout'})
        return jsonify({'status': 'ok', 'search_result': t.get_search_result()})
    return jsonify({'status': 'error', 'message': 'Session not found'})

@bp.route('/prev_page', methods=['GET'])
def prev_page():
    if 'id' in session:
        id = session['id']
        debug_log(f'prev_page: {id}')
        t = user_sessions[id]
        event = Event()
        t.send_msg(SearchThread.CMD_PREV_PAGE, None, event)
        if not event.wait(20):
            return jsonify({'status': 'error', 'message': 'Prev page timeout'})
        return jsonify({'status': 'ok', 'search_result': t.get_search_result()})
    return jsonify({'status': 'error', 'message': 'Session not found'}) 

@bp.route('/')
def main_page():
    return render_template('index.html')