import re
import io
import os.path
from glob import glob

from datetime import datetime, timedelta
from collections import OrderedDict

import PIL.Image

from . import app
from .datastore import Picture


def image_has_transparency(image):
    """
    Determine if an image has transparency, by checking
    its mode/metadata, or pixel values for RBGA

    """
    # easy enough
    if image.mode in ('RGB', 'L', '1', 'CMYK', 'YCbCr', 'I', 'F'):
        return False

    # seems to work with GIF/PNG
    if image.mode == 'P':
        return 'transparency' in image.info

    # a bit tricky, they mostly have transparent pixels
    # (due to optimizers saving images as RGB), but they may
    # as well have their entire alpha channel opaque
    if image.mode == "RGBA":
        _, _, _, (alphamin, _) = image.getextrema()
        return alphamin < 255

    return True

def create_preview(filename, image, size):
    """Creates a smaller static image, used for thumbnail and previews"""
    # Thumbnail starts here
    ext = "png" if image_has_transparency(image) else "jpg"
    filename += '.%s' % ext

    # thumbfilename = '%s%s.%s' % (prefix, uid, ext)
    # thumbpath = fspath_for_name(thumbfilename)

    image = image.copy()
    image.thumbnail((size, size), PIL.Image.ANTIALIAS)
    with io.open(filename, 'wb+') as output:
        if ext == "jpg":
            # In case of indexed palette, JPEG mut be converted to RGB
            image = image.convert('RGB')
            image.save(output, quality=75, optimize=True, progressive=True)
        else:  # png
            image.save(output, optimize=True)

    # thumbnail.close()
    image.close()
    return filename
    return output, ext

def request_wants_json(request):
    # http://flask.pocoo.org/snippets/45/
    best = request.accept_mimetypes.best_match(('application/json',
                                                'text/html'))
    return (
            best == 'application/json'
            and request.accept_mimetypes[best] >
                request.accept_mimetypes['text/html']
            )

def parse_timespec(value):
    if value == '-':
        return None

    units = OrderedDict((
        ('Y', timedelta(days=365)),
        ('M', timedelta(days=30)),
        ('D', timedelta(days=1)),
        ('h', timedelta(hours=1)),
        ('m', timedelta(minutes=1)),
        ('s', timedelta(seconds=1)),
    ))

    patterns = ('(?:(?P<%s>[0-9]+)%s)?' % (unit, unit) for unit in units)
    match = re.match('^%s$' % ''.join(patterns), value)

    if not match:
        raise ValueError('invalid time spec: %r' % value)

    ret = timedelta()
    for key, value in units.items():
        num = match.group(key)
        if num:
            ret += int(num) * value

    return ret


def cleanup_images():
    """Delete expired images, and images that where not fully created"""

    to_delete = Picture.for_cleanup()

    for image in to_delete:
        delete_image(image)

    Picture.delete_many(to_delete)

def delete_image(image):
    """Delete image at the filesystem level"""
    path = os.path.join(app.config['DATADIR'], image.uid[:2], image.uid) + '.*'

    for file in glob(path):
        os.remove(file)


@app.template_filter('time_since')
def time_since(value, default="moments ago"):
    diff = datetime.utcnow() - value

    ret = time_unit(diff)
    if ret == '':
        return default

    return '%s ago' % ret


def time_unit(value):
    if value is None:
        return 'Never'

    periods = (
        (value.days / 365, "year", "years"),
        (value.days / 30, "month", "months"),
        (value.days / 7, "week", "weeks"),
        (value.days, "day", "days"),
        (value.seconds / 3600, "hour", "hours"),
        (value.seconds / 60, "minute", "minutes"),
        (value.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        if period >= 1:
            return '%d %s' % (period, singular if period < 2 else plural)

    return ''  # < 1s


@app.template_filter('time_unit')
def time_unit_tmpl(value):
    value = parse_timespec(value)
    return time_unit(value)
