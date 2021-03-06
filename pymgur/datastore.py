import re
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
import random
import os.path

from flask import g

from . import app


def connect_db():
    """Connects to the specific database."""
    dbpath = os.path.join(app.config['DATADIR'], 'pymgur.db')
    create_db = not os.path.exists(dbpath)

    conn = sqlite3.connect(dbpath, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row

    # conn.execute('PRAGMA FOREIGN KEYS = ON;')

    if create_db:
        init_db()
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


def init_db():
    """Initializes the database."""
    # XXX Use locking mechanism to handle concurrent calls
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def gen_uid(length=8):
    ret = ''
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'

    # need at least one number
    while not re.search('[0-9]', ret):
        ret = ''.join(random.choice(chars) for _ in range(length))

    return ret


class Picture:
    id = None
    uid = None
    title = None
    author = None
    width = None
    height = None
    status = 0
    imageset = None
    extension = None
    thumb_extension = None
    secret = None
    remote_addr = None
    date_created = None
    date_expire = None

    ACTIVE = 1
    PRIVATE = 2
    HAS_THUMBNAIL = 4
    HAS_PREVIEW = 8
    DELETING = 16

    @classmethod
    def new(cls):
        conn = get_db()
        now = datetime.utcnow()
        secret = gen_uid(16)

        SQL = 'INSERT INTO pictures (uid, secret, date_created) ' \
              'VALUES (:uid, :secret, :date_created)'
        with closing(conn.cursor()) as cur:
            for _ in range(100):
                uid = gen_uid()
                data = {
                    'uid': uid,
                    'secret': secret,
                    'date_created': now,
                }

                try:
                    cur.execute(SQL, data)
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

    def __init__(self, **kwargs):
        # Used by retrieval method
        self.__dict__.update(kwargs)

    def save(self, commit=True):
        conn = get_db()

        update_clause = []
        for name in self.__dict__:
            if (not (name.startswith('_')
                     or re.match('^[_0-9a-z]+$', name)
                     or name == 'id')):
                continue
            update_clause.append(' %s = :%s' % (name, name))

        SQL = 'UPDATE pictures SET %s WHERE id=:id' % ','.join(update_clause)
        with closing(conn.cursor()) as cur:
            cur.execute(SQL, self.__dict__)

        if commit:
            conn.commit()

        return self

    @classmethod
    def by_uid(cls, uid):
        conn = get_db()

        search = {'uid': uid, 'now': datetime.utcnow(), 'active': cls.ACTIVE}

        SQL = 'SELECT * FROM pictures WHERE uid=:uid AND status & :active ' \
            'AND (date_expire IS NULL OR date_expire > :now)'
        with closing(conn.execute(SQL, search)) as cur:
            res = cur.fetchone()
            if not res:
                return None

            return cls(**res)

    @classmethod
    def latest(cls, limit=8, include_private=False):
        conn = get_db()

        search = {'active': cls.ACTIVE,
                  'private': cls.PRIVATE,
                  'now': datetime.utcnow(),
                  'limit': limit,
                  }

        SQL = 'SELECT * FROM pictures ' \
              'WHERE (date_expire IS NULL OR date_expire > :now) ' \
              'AND status & :active AND NOT status & :private ' \
              'ORDER BY date_created DESC LIMIT :limit'

        if include_private:
            search['private'] = 0

        with closing(conn.execute(SQL, search)) as cur:
            return [cls(**row) for row in cur]

    def delete(self):
        # XXX try pass
        from .utils import delete_image
        delete_image(self)

        # Delete in db
        SQL = 'DELETE FROM pictures WHERE id = :id'
        conn = get_db()
        conn.execute(SQL, {'id': self.id})
        conn.commit()

    @classmethod
    def delete_many(cls, images):
        SQL = 'DELETE FROM pictures WHERE id in (%s)'
        SQL %= ', '.join('?' * len(images))

        conn = get_db()
        conn.execute(SQL, [img.id for img in images])
        conn.commit()

    @classmethod
    def for_cleanup(cls):
        return cls._for_cleanup_expired() + cls._for_cleanup_misshap()

    @classmethod
    def _for_cleanup_generic(cls, query, params):
        conn = get_db()

        SQL_UPDATE = 'UPDATE pictures SET status = status | ? ' \
                     'WHERE id IN (%s)'

        ret = []
        cur = conn.cursor()
        try:
            cur.execute('begin immediate transaction')

            ret = [cls(**row) for row in cur.execute(query, params)]

            SQL_UPDATE %= ', '.join('?' * len(ret))

            params = [cls.DELETING] + [img.id for img in ret]

            cur.execute(SQL_UPDATE, params)
        finally:
            conn.commit()
            cur.close()

        return ret

    @classmethod
    def _for_cleanup_expired(cls):
        search = {'when': datetime.utcnow(), 'deleting': cls.DELETING}

        SQL_QUERY = 'SELECT * FROM pictures ' \
                    'WHERE NOT status & :deleting AND date_expire < :when'

        return cls._for_cleanup_generic(SQL_QUERY, search)

    @classmethod
    def _for_cleanup_misshap(cls):
        search = {'when': datetime.utcnow() - timedelta(minutes=20),
                  'status': cls.DELETING | cls.ACTIVE}

        SQL_QUERY = 'SELECT * FROM pictures ' \
                    'WHERE NOT status & :status AND date_created < :when'

        return cls._for_cleanup_generic(SQL_QUERY, search)

    def siblings(self):
        if not self.imageset:
            return []

        conn = get_db()
        search = {'id': self.id,
                  'active': self.ACTIVE,
                  'imageset': self.imageset,
                  'now': datetime.utcnow()}

        SQL = 'SELECT * FROM pictures WHERE imageset=:imageset ' \
            'AND status & :active AND id != :id ' \
            'AND (date_expire IS NULL OR date_expire > :now) ' \
            'ORDER BY id'

        with closing(conn.execute(SQL, search)) as cur:
            return [self.__class__(**row) for row in cur]

    @property
    def preview_width(self):
        value = int(self.width *
                    app.config['PREVIEW_SIZE'] / max(self.height, self.width))
        return value if value < self.width else self.width

    @property
    def preview_height(self):
        value = int(self.height *
                    app.config['PREVIEW_SIZE'] / max(self.height, self.width))
        return value if value < self.height else self.height


def create_imageset():
    """Creates a new imageset id and immediatelly delete it"""
    conn = get_db()
    with closing(conn.cursor()) as cur:
        cur.execute('INSERT INTO imagesets (id) VALUES(NULL)')
        ret = cur.lastrowid
        cur.execute('DELETE FROM imagesets WHERE id=:id', {'id': ret})

        conn.commit()
        return ret
