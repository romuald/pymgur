import io
import os
import os.path
import errno
import base64
from shutil import copyfileobj
from datetime import datetime


import PIL.Image
import werkzeug.exceptions
from flask import request, g, redirect, url_for, abort, render_template, \
    flash, jsonify, send_from_directory


from . import app
from .datastore import Picture, create_imageset, get_db
from .utils import (image_has_transparency, create_preview, request_wants_json,
                    parse_timespec, cleanup_images)


FORMATS = {'PNG', 'JPEG', 'GIF'}


def post_images():
    print("args", request.args)
    print("form", request.form)
    print("files", request.files)
    print("data", request.data)

    api = not request.form.get('from_web')
    if api:
        # API version: no private arg = default setting
        try:
            private = bool(request.form['private'])
        except (KeyError, ValueError):
            private = app.config['DEFAULT_PRIVATE']

    else:
        # Web version: no private arg = not private
        private = bool(request.form.get('private'))

    ttl = request.form.get('ttl')
    if not ttl:
        ttl = app.config['DEFAULT_TTL']

    ttl = parse_timespec(ttl)
    if ttl is not None and not ttl:
        # None is a valid result (no expiration), but 0 is not (expires now)
        ttl = parse_timespec(app.config['DEFAULT_TTL'])

    images = []

    for file in request.files.values():
        image = publish_image(file.stream)
        if image:
            print("Created image %s" % image.uid)
            images.append(image)

    b64i = 'base64,'
    for name, value in request.form.items():
        if name.startswith('bimage') and value:
            try:
                if b64i in value:
                    # data:xx/xxx;base64,
                    value = value[value.index(b64i) + len(b64i):]
                stream = io.BytesIO(base64.b64decode(value.encode()))
            except:
                raise

            image = publish_image(stream)
            if image:
                print("Created image %s from base64" % image.uid)
                images.append(image)


    if len(images) > 1:
        imageset = create_imageset()
    else:
        imageset = None

    expires = datetime.utcnow() + ttl if ttl else None

    for image in images:
        image.imageset = imageset
        author = request.form.get('author')
        if author:
            image.author = author[:30]

        if private:
            image.status |= image.PRIVATE

        if ttl:
            image.date_expire = expires
        print("Save image %s" % image.uid)
        image.save(commit=False)
    get_db().commit()

    if api:
        # XXX find a way to properly retrieve author / expiration data
        # - query string POST /?author=Sushi&ttl=3d
        # - JSON as one of the form data
        # - one of the post data
        ret = jsonify([
            {
                'uid': image.uid,
                'secret': image.secret,
                'href': url_for('image', uid=image.uid, _external=True),
            } for image in images
        ])
        ret.status_code = 201
        return ret

    if not images:
        return redirect(url_for('index'))  # XXX error, probably
    return redirect(url_for('image', uid=images[0].uid))


def publish_image(stream):
    image = Picture.new()

    if len(stream.read(1)) == 0:
        # Empty stream
        return None

    stream.seek(0)

    try:
        pimage = PIL.Image.open(stream)
    except Exception as exc:
        # XXX log.exception
        print("Could not load image")
        return None

        res = jsonify(error='Could not load image')
        res.status_code = 400
        return res

    if pimage.format not in FORMATS:
        print('Unhandled image format: %s' % (pimage.format, ))
        return None
        res = jsonify(error='Unhandled image format: %s' % (pimage.format, ))
        res.status_code = 400
        return res

    image.width = pimage.width
    image.height = pimage.height

    basedir = os.path.join(app.config['DATADIR'], image.uid[:2])
    try:
        os.mkdir(basedir)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise

    stream.seek(0)
    ext = pimage.format.lower()

    # keep filenames consistant
    if ext == 'jpeg':
        ext = 'jpg'

    fullname = os.path.join(basedir, '%s.%s' % (image.uid, ext))
    with io.open(fullname, 'wb+') as output:
        copyfileobj(stream, output)


    psize = app.config['PREVIEW_SIZE']
    tsize = app.config['THUMBNAIL_SIZE']
    if image.width > tsize or image.height > tsize:
        image.status |= image.HAS_THUMBNAIL
        fullname = os.path.join(basedir, '%s.t' % image.uid)
        fullname = create_preview(fullname, pimage, tsize)

        image.thumb_extension = fullname[fullname.rindex('.') + 1:]

    if image.width > psize or image.height > psize:
        image.status |= image.HAS_PREVIEW
        fullname = os.path.join(basedir, '%s.p' % image.uid)

        fullname = create_preview(fullname, pimage, psize)
        image.thumb_extension = fullname[fullname.rindex('.') + 1:]


    image.status |= image.ACTIVE
    image.extension = ext

    return image

@app.route('/', methods=('GET', 'POST'))
def index():

    if request.method == 'POST':
        cleanup_images()
        return post_images()

    latest = Picture.latest()

    # Cache the "render" of URL for as it is relatively slow
    i_href = url_for('image', uid='__uid__')
    t_href = url_for('image_thumbnail', uid='__uid__')

    def image_href(image):
        return i_href.replace('__uid__', image.uid)

    def thumbnail_href(image):
        return t_href.replace('__uid__', image.uid)

    ret = render_template('index.html',
                           latest=latest,
                           image_href=image_href,
                           thumbnail_href=thumbnail_href,
                           thumbnail_size=app.config['THUMBNAIL_SIZE'])

    return ret


@app.route('/<uid>', methods=('GET', 'POST', 'PUT', 'DELETE'))
def image(uid):
    if request_wants_json(request):
        return image_as_json(uid)

    image = Picture.by_uid(uid)
    if not image:
        abort(404)

    return render_template('image.html', image=image)

def image_as_json(uid):
    image = Picture.by_uid(uid)
    if not image:
        # XXX error as JSON
        abort(404)

    siblings = [url_for('image', uid=sibling.uid, _external=True)
        for sibling in image.siblings()]

    data = {
        'uid': image.uid,
        'author': image.author,
        'title': image.title,
        'private': bool(image.status & image.PRIVATE),
        'date_created': image.date_created,
        'date_expire': image.date_expire,
        'href': url_for('image', uid=image.uid, _external=True),
        'image_href': url_for('image_full', uid=image.uid, _external=True),
        'siblings': siblings,
        'preview_href': None,
        'thumbnail_href': None,
    }

    if image.status & image.HAS_PREVIEW:
        data['preview_href'] = url_for('image_preview',
                                       uid=image.uid, _external=True)
    if image.status & image.HAS_THUMBNAIL:
        data['thumbnail_href'] = url_for('image_thumbnail',
                                         uid=image.uid, _external=True)

    return jsonify(data)


def image_render(uid, suffix, fallback):
    image = Picture.by_uid(uid)
    if not image:
        abort(404)

    filename = '%s%s' % (image.uid, suffix % image.__dict__)

    path = os.path.join(app.config['DATADIR'], image.uid[:2])

    try:
        return send_from_directory(path, filename)
    except werkzeug.exceptions.NotFound:
        if fallback:
            return redirect(url_for(fallback, uid=image.uid), code=301)
        raise

@app.route('/i/<uid>')
def image_full(uid):
    return image_render(uid, '.%(extension)s', None)

@app.route('/p/<uid>')
def image_preview(uid):
    return image_render(uid, '.p.%(thumb_extension)s', 'image_full')


@app.route('/t/<uid>')
def image_thumbnail(uid):
    return image_render(uid, '.t.%(thumb_extension)s', 'image_preview')
