import os
import os.path
import re
import ast
import random
import argparse
import configparser

from pprint import pprint
from datetime import datetime, timedelta
from contextlib import closing
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from werkzeug.contrib.fixers import ProxyFix


app = Flask(__name__)


def boolean(value):
    if value.lower() in ('true', 't', 'yes', 'y'):
        return True

    if value.lower() in ('false', 'f', 'no', 'n'):
        return False

    raise ValueError('Invalid boolean value: %r' % value)


def config_value(key, value):
    if value == '':
        return None

    return {'TEMPLATES_AUTO_RELOAD': boolean,
            'MAX_CONTENT_LENGTH': int,
            'PREVIEW_SIZE': int,
            'THUMBNAIL_SIZE': int,
            'DEFAULT_PRIVATE': boolean,
            'MAX_IMAGES': int,
            'PROXIES': int,
            'JPEG_QUALITY': int,
        }.get(key.upper(), str)(value)


def parse_args():
    parser = argparse.ArgumentParser(description='TBD')

    parser.add_argument('--config', '-c', type=argparse.FileType('r'))

    return parser.parse_args()


def configure():
    args = parse_args()

    mydir = os.path.dirname(__file__)

    cparser = configparser.ConfigParser()
    cparser.read(os.path.join(mydir, 'pymgur.default.ini'))

    if args.config:
        cparser.read_string(args.config.read())

    section = cparser['pymgur']
    section.update({
        'app_root_path': mydir,
        'run_path': os.getcwd()
    })
    values = {k.upper(): config_value(k, v) for k, v in section.items()}

    # TTLS is a list
    values['TTLS'] = [value.strip() for value in values['TTLS'].split(',')]

    app.config.update(values)

    # Workaround Flask issue
    app.jinja_env.auto_reload = values['TEMPLATES_AUTO_RELOAD']


from . import datastore
from . import views

def main():
    """Dev runner"""
    configure()

    if app.config['PROXIES'] > 0:
        app.wsgi_app = ProxyFix(app.wsgi_app, app.config['PROXIES'])
    app.run(use_reloader=True, threaded=True)
