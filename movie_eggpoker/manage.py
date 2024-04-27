from flask import Blueprint, render_template, jsonify
from . import get_logger, debug_log
from dataclasses import dataclass
from . import video_search

bp = Blueprint('manage', __name__)

@bp.route('/manage', methods=['GET'])
def manage():
    num_search_threads = len(video_search.user_sessions)
    return render_template('manage.html', num_search_threads=num_search_threads)