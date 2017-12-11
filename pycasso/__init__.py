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
    'SECRET_KEY': 'plokiploki',
    'TEMPLATES_AUTO_RELOAD': True,
    'MAX_CONTENT_LENGTH': 48 * 1024 * 1024,
})
# app.config.from_envvar('PYCASSO_SETTINGS', silent=True)
from . import datastore
from . import views



def gen_uid(length=8):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    ret = ''.join(random.choice(chars) for _ in range(length))
    if not re.search('[0-9]', ret):
        return gen_uid(length)
    return ret
"""
def new_image():
    conn = get_db()
    now = datetime.utcnow()
    with closing(conn.cursor()) as cur:
        for _ in range(100):
            uid = gen_uid()
            data = {
                'uid': uid,
                'secret': gen_uid(16),
                'date_created': now,
            }
            
            try:
                cur.execute('INSERT INTO photos (uid, secret, date_created) '
                    'VALUES (:uid, :secret, :date_created)', data)
            except sqlite3.IntegrityError:
                continue
            iid = cur.lastrowid
            conn.commit()

            break
        else:
            raise RuntimeError('unable to generate a new uid')

    return (uid, iid)
"""

def post_image():
    # img = new_image()
    img = Picture.new()
    return '-'.join(map(str, (img.id, img.uid)))

