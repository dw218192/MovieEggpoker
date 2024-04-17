from flask import Blueprint, render_template
import requests
import xml.etree.ElementTree as ET

bp = Blueprint('main', __name__)
RTMP_STATS_URL = 'http://movies.eggpoker.com/stat.xml'

@bp.route('/')
def main_page():
    return render_template('index.html')