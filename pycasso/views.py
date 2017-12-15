import io
import os
import os.path
import errno
from shutil import copyfileobj


import PIL.Image
import werkzeug.exceptions
from flask import request, g, redirect, url_for, abort, render_template, \
    flash, jsonify, send_from_directory


from . import app
from .datastore import Picture, create_imageset, get_db
from .utils import image_has_transparency, create_preview, request_wants_json


FORMATS = {'PNG', 'JPEG', 'GIF'}


def post_images():
    print("args", request.args)
    print("form", request.form)
    print("files", request.files)
    print("data", request.data)

    api = not request.form.get('from_web')

    images = []
    
    for file in request.files.values():
        image = publish_image(file)
        images.append(image)

    if len(images) > 1:
        imageset = create_imageset()
    else:
        imageset = None

    for image in images:
        image.author = request.form.get('author')
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

def publish_image(file):
    image = Picture.new()
    stream = file.stream

    try:
        pimage = PIL.Image.open(stream)
    except Exception as exc:
        # XXX log.exception
        res = jsonify(error='Could not load image')
        res.status_code = 400
        return res

    if pimage.format not in FORMATS:
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


    if image.width > 200 or image.height > 200:
        image.status |= image.HAS_THUMBNAIL
        fullname = os.path.join(basedir, '%s.t' % image.uid)
        fullname = create_preview(fullname, pimage, 200)

        image.thumb_extension = fullname[fullname.rindex('.') + 1:]

    if image.width > 800 or image.height > 800:
        image.status |= image.HAS_PREVIEW
        fullname = os.path.join(basedir, '%s.p' % image.uid)

        fullname = create_preview(fullname, pimage, 800)
        image.thumb_extension = fullname[fullname.rindex('.') + 1:]


    image.status |= image.ACTIVE
    image.extension = ext

    return image


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        return post_images()

    return render_template('index.html')


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
