import os
import argparse
import configparser

from pprint import pprint  # noqa

from flask import Flask
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

    return {
            'TEMPLATES_AUTO_RELOAD': boolean,
            'MAX_CONTENT_LENGTH': int,
            'PREVIEW_SIZE': int,
            'THUMBNAIL_SIZE': int,
            'DEFAULT_PRIVATE': boolean,
            'MAX_IMAGES': int,
            'PROXIES': int,
            'JPEG_QUALITY': int,
            'DEBUG': boolean,
        }.get(key.upper(), str)(value)


def parse_args():
    parser = argparse.ArgumentParser(description='TBD')

    parser.add_argument('--config', '-c', type=argparse.FileType('r'),
                        help='Configuration file')
    parser.add_argument('--datadir', '-d',
                        help='data directory (overwritten from configuration)')

    return parser.parse_args()


def configure():
    args = parse_args()

    mydir = os.path.abspath(os.path.dirname(__file__))

    cparser = configparser.ConfigParser()
    cparser.read(os.path.join(mydir, 'pymgur.default.ini'))

    config_file = None

    if args.config:
        config_file = args.config
    elif os.environ.get('PYMGUR_CONFIG'):
        config_file = open(os.environ['PYMGUR_CONFIG'])

    if config_file:
        print('Using configuration: %r'  % config_file.name)
        cparser.read_string(config_file.read())
    else:
        print('Using default configuration')

    section = cparser['pymgur']
    section.update({
        'app_root_path': mydir,
        'run_path': os.getcwd()
    })

    if args.datadir:
        if not os.path.isdir(args.datadir):
            raise RuntimeError('directory %r does not exists' % args.datadir)

        section.update({'datadir': args.datadir})
    values = {k.upper(): config_value(k, v) for k, v in section.items()}

    # TTLS is a list
    values['TTLS'] = [value.strip() for value in values['TTLS'].split(',')]

    app.config.update(values)


configure()

from . import datastore  # noqa
from . import views  # noqa
from .template_filters import noop  # noqa

def main():
    """Dev runner"""

    if app.config['PROXIES'] > 0:
        app.wsgi_app = ProxyFix(app.wsgi_app, app.config['PROXIES'])
    app.run(use_reloader=True, threaded=True)
