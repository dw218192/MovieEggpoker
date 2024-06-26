from flask import Blueprint, render_template, request, jsonify, current_app, session, app, g

from . import debug_log, info, UserSession, tick_func
from dataclasses import dataclass
from youtubesearchpython import VideosSearch, Video
from typing import Optional
from threading import Thread, Event, Lock
import queue
import re
import datetime
from .consts import SESSION_TIMEOUT

bp = Blueprint('video', __name__)
g_session_to_thread : dict[UserSession, 'SearchThread'] = {}

# Regular expression pattern to match various YouTube URL formats
g_ytb_url_pattern = re.compile(r'^.*(youtu.be/|v/|u/\w/|embed/|watch\?v=|shorts/&v=)([^#&?]*).*')
g_service_lock = Lock()

@tick_func
def tick():
    debug_log('tick: video_search')
    with g_service_lock:
        now = datetime.datetime.now()
        to_del = []
        for usr_session, t in g_session_to_thread.items():
            if (now - usr_session.last_active).total_seconds() > SESSION_TIMEOUT:
                info(f'inactive session: {usr_session.id}')
                if usr_session in g_session_to_thread:
                    event = Event()
                    t = g_session_to_thread[usr_session]
                    t.send_msg(SearchThread.CMD_STOP, None, event)
                    to_del.append(usr_session)
        for usr_session in to_del:
            del g_session_to_thread[usr_session]

def handle_video(video : dict) -> 'SearchResultItem':
    width,height = 1080,720
    if len(video['thumbnails']) > 0:
        url = video['thumbnails'][0]['url']
    else:
        url = 'https://via.placeholder.com/640x480.png?text=No+thumbnail+found'
    return SearchResultItem(
        title = video['title'],
        url = video['link'],
        thumbnail = url,
        width = width,
        height = height
    )

def get_thread(ses : UserSession) -> 'SearchThread':
    if ses in g_session_to_thread:
        return g_session_to_thread[ses]
    debug_log(f'Creating new search thread for {ses.id}')
    
    t = SearchThread(ses)
    g_session_to_thread[ses] = t
    t.start()
    return t

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

    def __init__(self, user_session : UserSession) -> None:
        super().__init__()
        self.msg_queue = queue.Queue()
        self.search_query = ''

        # pages of search results
        self.cur_page = 0
        self.search_result : list[list[SearchResultItem]] = []
        self.search_engine : Optional[VideosSearch] = None
        self.user_session = user_session

    def _handle_res(self, res: dict) -> list[SearchResultItem]:
        search_result = []
        for video in res['result']:
            search_result.append(handle_video(video))
        return search_result
    
    def _cmd_search(self, search_query: str) -> None:
        self.search_engine = VideosSearch(search_query, limit = 10)
        self.search_query = search_query
        self.cur_page = 0
        self.search_result = [self._handle_res(self.search_engine.result())]

    def _recover_search(self) -> None:
        return self._cmd_search(self.search_query)
    
    def _cmd_next_page(self, _) -> None:
        if self.search_engine is None:
            self._recover_search()
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
    
    def _cmd_prev_page(self, _) -> None:
        if self.search_engine is None:
            self._recover_search()
        else:
            if self.cur_page > 0:
                self.cur_page -= 1
            else:
                debug_log('No more search results')

    def run(self):
        CMD_MAP = {
            SearchThread.CMD_SEARCH: SearchThread._cmd_search,
            SearchThread.CMD_NEXT_PAGE: SearchThread._cmd_next_page,
            SearchThread.CMD_PREV_PAGE: SearchThread._cmd_prev_page,
        }
        
        while True:
            # get a message from the queue
            cmd, msg, event = self.msg_queue.get()
            if cmd == self.CMD_STOP:
                event.set()
                break
            elif cmd in CMD_MAP:
                CMD_MAP[cmd](self, msg)
            else:
                debug_log(f'Invalid command: {cmd}')
            event.set()

    def get_search_result(self):        
        return self.search_result[self.cur_page]

    def send_msg(self, cmd, msg, event : Event):
        self.msg_queue.put((cmd, msg, event))

@bp.route('/search_video', methods=['GET'])
def search_video_v2():
    search_query = request.args.get('searchInput')
    if g_ytb_url_pattern.match(search_query):
        # user entered a YouTube URL, just return the video
        # extract the id
        search_query = g_ytb_url_pattern.match(search_query).group(2)
        video = Video.getInfo(search_query)
        if video:
            return jsonify({'status': 'ok', 'html': render_template('search_result.html', videos=[handle_video(video)])})
        else:
            return jsonify({'status': 'error', 'html': '<li>Video not found</li>'})

    with g_service_lock:
        usr_session = UserSession(session)
        t = get_thread(usr_session)

        usr_session.keep_alive()
        info(f"{usr_session.id}: search_video: {search_query}")
        event = Event()
        t.send_msg(SearchThread.CMD_SEARCH, search_query, event)

        if not event.wait(20):
            return jsonify({'status': 'error', 'html': '<li>Search timeout</li>'})
        return jsonify({'status': 'ok', 'html': render_template('search_result.html', videos=t.get_search_result())})

@bp.route('/user_disconnected', methods=['GET'])
def user_disconnected():
    if UserSession.is_valid(session):
        usr_session = UserSession(session)
        if usr_session in g_session_to_thread:
            with g_service_lock:
                event = Event()
                t = g_session_to_thread[usr_session]
                t.send_msg(SearchThread.CMD_STOP, None, event)
                del g_session_to_thread[usr_session]
        usr_session.delete()
    return jsonify({'status': 'ok'})

@bp.route('/next_page', methods=['GET'])
def next_page():
    if UserSession.is_valid(session):
        with g_service_lock:
            usr_session = UserSession(session)
            t = get_thread(usr_session)
            usr_session.keep_alive()

            info(f'next_page: {usr_session.id}')
            event = Event()
            t.send_msg(SearchThread.CMD_NEXT_PAGE, None, event)
            if not event.wait(20):
                return jsonify({'status': 'error', 'html': '<li>Next page timeout</li>'})
            return jsonify({'status': 'ok', 'html': render_template('search_result.html', videos=t.get_search_result())})
    return jsonify({'status': 'error', 'html': '<li>Session not found</li>'})

@bp.route('/prev_page', methods=['GET'])
def prev_page():
    if UserSession.is_valid(session):
        with g_service_lock:
            usr_session = UserSession(session)
            t = get_thread(usr_session)
            info(f'prev_page: {usr_session.id}')
            event = Event()
            t.send_msg(SearchThread.CMD_PREV_PAGE, None, event)
            if not event.wait(20):
                return jsonify({'status': 'error', 'html': '<li>Prev page timeout</li>'})
            return jsonify({'status': 'ok', 'html': render_template('search_result.html', videos=t.get_search_result())})
    return jsonify({'status': 'error', 'html': '<li>Session not found</li>'})

@bp.route('/')
def main_page():
    return render_template('index.html')