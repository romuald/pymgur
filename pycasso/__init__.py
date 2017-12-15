import os
import re
import random
from pprint import pprint
from datetime import datetime, timedelta
from contextlib import closing
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash

# from .datastore import Picture



app = Flask(__name__)
app.config.update({
    'DATADIR': os.path.join(app.root_path, 'data'),
    'SECRET_KEY': 'plokiploki',  # should not be used (yet)
    'TEMPLATES_AUTO_RELOAD': True,
    'MAX_CONTENT_LENGTH': 48 * 1024 * 1024,
    'PREVIEW_SIZE': 800,  # in pixels
    'THUMBNAIL_SIZE':  200,  # ditto
})

# app.config.from_envvar('PYCASSO_SETTINGS', silent=True)
from . import datastore
from . import views

