from flask import Blueprint, render_template, request, jsonify, current_app, session

from . import get_logger, debug_log
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from yt_dlp import YoutubeDL, utils
from typing import Optional


bp = Blueprint('main', __name__)

@dataclass
class SearchResultItem:
    title: str
    url: str
    thumbnail: str
    width : int
    height : int

def perform_search(search_query, max_results = 20):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'flat_playlist': True,
        'skip_download': True,
#        'match_filter': utils.match_filter_func("original_url!*=/shorts/ & url!*=/shorts/"),
        'geo_bypass' : True,
        'logger' : get_logger(),
    }
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'ytsearch{str(max_results)}:{search_query}')
    search_results = []
    if 'entries' in result:
        for entry in result['entries']:
            thumbnail = entry['thumbnails'][0]
            item = SearchResultItem(
                entry['title'],
                entry['url'],
                thumbnail['url'],
                thumbnail['width'],
                thumbnail['height']
            )
            search_results.append(item)
            debug_log(f"Found video: {entry}")
    return search_results

@bp.route('/search_video', methods=['GET'])
def search_video():
    search_query = request.args.get('searchInput')
    search_results = perform_search(search_query)
    return jsonify(search_results)

@bp.route('/')
def main_page():
    return render_template('index.html')