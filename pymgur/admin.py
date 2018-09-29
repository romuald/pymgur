"""
admin views
"""


from crypt import crypt
from hmac import compare_digest


from . import app

from flask import request, redirect, url_for, abort, render_template, \
    jsonify, send_from_directory, make_response, session


@app.route('/admin/', methods=('GET', 'POST'))
def admin_index():
    if not app.config['ADMIN_PASSWORD']:
        return redirect(url_for('admin_nopass'))

    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    return 'i am index'


@app.route('/admin/login', methods=('GET', 'POST'))
def admin_login():
    if request.form.get('password'):
        ours = app.config['ADMIN_PASSWORD']
        if ours.strip().startswith('$'):
            ours = ours.strip()
            if compare_digest(crypt(request.form['password'], ours), ours):
                session['logged_in'] = True
                return redirect(url_for('admin_index'))
        else:
            return 'TBD'
        return 'invalid password'

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', False)
    return redirect(url_for('admin_login'))


@app.route('/admin/setuppass', methods=('GET', 'POST'))
def admin_nopass():
    if app.config['ADMIN_PASSWORD']:
        return redirect(url_for('admin_index'))

    if request.form.get('password'):
        hashed = crypt(request.form.get('password'))
    else:
        hashed = None
    return render_template('admin_nopass.html', hashed=hashed)