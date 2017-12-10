import re
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
import random
import os.path

from flask import Flask, request, session, g

from . import app


def connect_db():
    """Connects to the specific database."""
    dbpath = os.path.join(app.config['DATADIR'], 'pycasso.db')
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row

    # conn.execute('PRAGMA FOREIGN KEYS = ON;')

    return conn

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def gen_uid(length=8):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    ret = ''.join(random.choice(chars) for _ in range(length))
    if not re.search('[0-9]', ret):
        return gen_uid(length)
    return ret

class Picture:
    id = None
    uid = None
    author = None
    height = None
    width = None
    status = 0
    secret = None
    date_created = None
    date_expire = None

    @classmethod
    def new(cls):
        conn = get_db()
        now = datetime.utcnow()
        secret = gen_uid(16)
        with closing(conn.cursor()) as cur:
            for _ in range(100):
                uid = gen_uid()
                data = {
                    'uid': uid,
                    'secret': gen_uid(16),
                    'date_created': now,
                }
                
                try:
                    cur.execute('INSERT INTO pictures (uid, secret, date_created) '
                        'VALUES (:uid, :secret, :date_created)', data)
                except sqlite3.IntegrityError:
                    continue
                data['id'] = cur.lastrowid
                conn.commit()

                break
            else:
                raise RuntimeError('unable to generate a new uid')
        self = cls()
        self.__dict__.update(data)

        return self
        # return (uid, iid)