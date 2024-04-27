from flask import Blueprint, render_template, request, jsonify, current_app, session, app, g
import requests
import xml.etree.ElementTree as ET
from . import get_logger, debug_log
from dataclasses import dataclass


STREAM_HOST_NAME = "movies.eggpoker.com"
bp = Blueprint('stream', __name__)


@dataclass
class StreamDesc:
    name: str
    app_name: str
    width: int
    height: int

@bp.route('/fetch_streams', methods=['GET'])
def fetch_active_streams():
    # url = f"https://{STREAM_HOST_NAME}/stat"
    # res = requests.get(url)
    # xml = res.text
    # try:
    #     root = ET.fromstring(xml)
    #     if root is None:
    #         raise ET.ParseError("Failed to parse XML")
    # except ET.ParseError as e:
    #     get_logger().error(f"Failed to parse XML: {e}")
    #     return jsonify({'status' : 'error', 'html' : f'Failed to parse XML: {xml}'})

    # stream_dict : dict[str, list[StreamDesc]] = {}
    # for appl in root.find('.//rtmp/server/application'):
    #     app_name = appl.find('name').text
    #     if app_name == 'private':
    #         continue  # Skip 'private' application
    #     live = appl.find('live')
    #     streams = live.findall('stream')

    #     for stream in streams:
    #         stream_name = stream.find('name').text
    #         meta = stream.find('meta')
    #         width = int(meta.find('width').text)
    #         height = int(meta.find('height').text)
    #         if app_name not in stream_dict:
    #             stream_dict[app_name] = []
    #         stream_dict[app_name].append(StreamDesc(stream_name, app_name, width, height))

    # generate some test data
    return jsonify({'status' : 'ok', 
                    'html' : render_template('stream_list.html', streams_grouped_by_app=
                                             {'test_app' : [StreamDesc('test_stream', 'test_app', 1920, 1080), 
                                                            StreamDesc('test_stream2', 'test_app', 1920, 1080)],
                                              'test_app2' : [StreamDesc('test_stream2', 'test_app2', 1920, 1080)]})})
    return jsonify({'status' : 'ok', 
                    'html' : render_template('stream_list.html', streams_grouped_by_app=stream_dict)})