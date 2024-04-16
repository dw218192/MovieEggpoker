from flask import Blueprint, render_template
import requests
import xml.etree.ElementTree as ET

bp = Blueprint('main', __name__)
RTMP_STATS_URL = 'http://movies.eggpoker.com/stat.xml'

def get_active_stream_paths():
    # Fetch the XML data from the Nginx RTMP stats page
    response = requests.get(RTMP_STATS_URL)
    if response.status_code == 200:
        # Parse the XML
        root = ET.fromstring(response.content)
        active_streams = []
        # Iterate over the stream nodes
        for stream in root.iter('stream'):
            # Get the stream path
            stream_path = stream.find('name').text
            # Append the stream path to the list
            active_streams.append(stream_path)
        return active_streams
    else:
        print("Failed to retrieve rtmp stat data")
        return []

@bp.route('/')
def main_page():
    render_template('index.html', channels=get_active_stream_paths())