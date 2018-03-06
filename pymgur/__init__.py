import os
import re
import random
from pprint import pprint
from datetime import datetime, timedelta
from contextlib import closing
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash
from werkzeug.contrib.fixers import ProxyFix


app = Flask(__name__)
app.config.update({
    'DATADIR': os.path.join(app.root_path, 'data'),
    # 'SECRET_KEY': 'plokiploki',  # should not be used (yet)
    'TEMPLATES_AUTO_RELOAD': True,
    'MAX_CONTENT_LENGTH': 48 * 1024 * 1024,
    'PREVIEW_SIZE': 800,  # in pixels
    'THUMBNAIL_SIZE':  200,  # ditto
    'DEFAULT_PRIVATE': False,
    'DEFAULT_TTL': '7D', # YMDhms, cumulative (eg: 1M15D -> 35 days)
    'MAX_TTL': None,  # ditto, may be None for no maximum
    'MAX_IMAGES': 8,  # maximum number of images in an imageset
    'TTLS': ['10s', '1h', '3h', '6h', '1D', '3D', '7D', '1M', '3M', '6M', '-'],
    'PROXIES': 1,
    'JPEG_QUALITY': 90,
})

if app.config['PROXIES'] > 0:
    app.wsgi_app = ProxyFix(app.wsgi_app, app.config['PROXIES'])

# app.config.from_envvar('PYCASSO_SETTINGS', silent=True)
from . import datastore
from . import views

def main():
    """Dev runner"""
    app.run(use_reloader=True, threaded=True)
