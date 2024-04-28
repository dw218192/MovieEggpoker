from flask import Blueprint, render_template, jsonify
from . import get_logger, debug_log
from dataclasses import dataclass
from . import video_search

bp = Blueprint('manage', __name__)

@bp.route('/manage', methods=['GET'])
def manage():
    return render_template('manage.html')

@bp.route('/manage/api/info', methods=['GET'])
def manage_api_info():
    num_search_threads = len(video_search.user_sessions)
    return jsonify({'status': 'ok', 'data': f'Active search threads: {num_search_threads}'})