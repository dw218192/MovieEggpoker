from flask import Blueprint, render_template, jsonify, current_app
from . import video_search
from .consts import LOG_FILE_PATH, MAX_LOG_LINES

bp = Blueprint('manage', __name__)

@bp.route('/manage', methods=['GET'])
def manage():
    return render_template('manage.html')

@bp.route('/manage/api/info', methods=['GET'])
def manage_api_info():
    num_search_threads = len(video_search.g_session_to_thread)
    # read logs from the end, upto MAX_LOG_LINES
    with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) > MAX_LOG_LINES:
        lines = lines[-MAX_LOG_LINES:]
    log_str = ''.join(lines)
    return jsonify({'status': 'ok', 'data': f'Active search threads: {num_search_threads}\n\nLOGS:\n{log_str}'})