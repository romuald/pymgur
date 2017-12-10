from . import app
from .datastore import Picture

from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash


def post_image():
    # img = new_image()
    img = Picture.new()
    return '-'.join(map(str, (img.id, img.uid)))

@app.route('/', methods=('GET', 'POST'))
def index():

    if request.method == 'POST':
        return post_image()

    return 'TBD'