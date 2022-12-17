import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from markupsafe import escape
from cert2grade.auth import login_required
from cert2grade.db import get_db

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    req_history = db.execute(
        'SELECT * FROM requests WHERE user_id = ?', (session['user_id'],)
    ).fetchall()
    return render_template('index.html', req_history=req_history)

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        raise Exception

@bp.route('/delete_req', methods=['POST'])
@login_required
def delete_req():
    req_codes = request.form['req_codes'].split('|')
    repl_str = '?,'*len(req_codes)
    repl_str = repl_str[:-1]
    query = 'DELETE FROM requests WHERE user_id = ? AND code IN (' + repl_str + ')'
    success = True
    try:
        db = get_db()
        db.execute(query, (session['user_id'], *req_codes))
        db.commit()
        affectedRows = db.execute('SELECT changes()').fetchone()[0]
        if affectedRows == 0: raise Exception
    except:
        success = False
    return json.dumps({'success': success}), 200, {'ContentType': 'application/json'}

@bp.route('/<req_code>', methods=['GET', 'POST'])
def show_req(req_code):
    code = escape(req_code)
    db = get_db()
    try:
        req = db.execute(
            'SELECT * FROM requests WHERE user_id = ? AND code = ?',
            (session['user_id'], code)
        ).fetchone()
    except:
        # failed to fetch the request, either becasue 
        # 1) the code doesn't exist
        # 2) the user doesn't have a req with that code
        return render_template('404.html') 
    if req['duration'] > 0:
        # the req has completed
        files = db.execute(
            'SELECT * FROM files WHERE request_id = ?', (req['request_id'],)
        ).fetchall()
        return render_template('view_results.html', req_code=code, files=files)
    elif req['duration'] == -1:
        # in uploading / churning phase
        return render_template('upload.html', req_code=code)
