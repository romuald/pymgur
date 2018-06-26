import re
import io
import os.path
from glob import glob

from datetime import timedelta
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


def get_exif(image):
    """Retrieve EXIF data (or not) from a PIL.Image"""
    return image._getexif() if hasattr(image, '_getexif') else None

def exif_transpose(image, exif_data):
    """Rotate / transpose a thumbnal according to the EXIF metadata

    Thanks to https://beradrian.wordpress.com/2008/11/14/rotate-exif-images/
    """

    operations = (
        (0, None),
        (0, PIL.Image.FLIP_LEFT_RIGHT),
        (-180, None),
        (0, PIL.Image.FLIP_TOP_BOTTOM),
        (-90, PIL.Image.FLIP_LEFT_RIGHT),
        (-90, None),
        (90, PIL.Image.FLIP_LEFT_RIGHT),
        (90, None),
    )
    orientation = exif_data and exif_data.get(274)

    if not orientation:
        return image

    try:
        rotate, transpose = operations[orientation - 1]
    except IndexError:
        # Invalid orientation in EXIF data
        return image

    if rotate:
        image = image.rotate(rotate, expand=True)

    if transpose:
        image = image.transpose(transpose)

    return image

def image_dimentions(image):
    """
    Retrieve the image dimentions, transposing width/height according to the
    EXIF metadata

    :type image: PIL.Image

    :return: tuple (width, height)
    """

    width, height = image.width, image.height

    exif = image._getexif()
    orientation = exif and exif.get(274)  # False if no exif data

    if orientation in (5, 6, 7, 8):
        width, height = height, width

    return width, height

def create_preview(filename, image, size):
    """Creates a smaller static image, used for thumbnail and previews"""
    # Thumbnail starts here
    ext = "png" if image_has_transparency(image) else "jpg"
    filename += '.%s' % ext

    # thumbfilename = '%s%s.%s' % (prefix, uid, ext)
    # thumbpath = fspath_for_name(thumbfilename)

    # Get EXIF from original image (EXIF data is not copied)
    exif = get_exif(image)

    image = image.copy()

    image.thumbnail((size, size), PIL.Image.ANTIALIAS)
    # Transpose after thumbnail (performance over quality)
    image = exif_transpose(image, exif)

    with io.open(filename, 'wb+') as output:
        if ext == "jpg":
            # In case of indexed palette, JPEG mut be converted to RGB
            image = image.convert('RGB')
            image.save(output, quality=app.config['JPEG_QUALITY'],
                       optimize=True, progressive=True)
        else:
            # PNG
            image.save(output, optimize=True)

    image.close()
    return filename


def request_wants_json(request):
    # http://flask.pocoo.org/snippets/45/
    best = request.accept_mimetypes.best_match(('application/json',
                                                'text/html'))
    return (
            best == 'application/json'
            and request.accept_mimetypes[best] >
                request.accept_mimetypes['text/html']
            )  # noqa


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
