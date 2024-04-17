from flask import Blueprint, render_template
import requests
import xml.etree.ElementTree as ET

bp = Blueprint('main', __name__)

@bp.route('/')
def main_page():
    return render_template('index.html')