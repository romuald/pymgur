from . import app

from .utils import time_unit, parse_timespec
from datetime import datetime

noop = object()


@app.template_filter('time_since')
def time_since(value, default="moments ago"):
    diff = datetime.utcnow() - value

    ret = time_unit(diff)
    if ret == '':
        return default

    return '%s ago' % ret


@app.template_filter('time_unit')
def time_unit_tmpl(value):
    value = parse_timespec(value)
    return time_unit(value)
