import json
import shortuuid
from datetime import datetime
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
        'SELECT * FROM requests WHERE user_id = ? ORDER BY timestamp DESC', (session['user_id'],)
    ).fetchall()
    json_req_history = [dict((req.keys()[k],v) for k,v in enumerate(req)) for req in req_history]
    for req in json_req_history:
        int_timestamp = req['timestamp']
        formatted_timestamp = datetime.fromtimestamp(int_timestamp).strftime('%d-%m-%Y %H:%M:%S')
        req['timestamp'] = formatted_timestamp
    return render_template('index.html', req_history=json_req_history)

@login_required
def create_req():
    user_id = session['user_id']
    req_code = shortuuid.ShortUUID().random(length=6)
    timestamp = datetime.now().timestamp()
    files = len(request.files)
    size = '' # not sure of the full size yet
    duration = -1 # since the upload is in progress
    query = 'INSERT INTO requests (user_id, code, timestamp, files, size, duration) VALUES (?, ?, ?, ?, ?, ?)'
    try:
        db = get_db()
        db.execute(query, (user_id, req_code, timestamp, files, size, duration))
        db.commit()
    except:
        return 'failed'
    return {
        'user_id': user_id,
        'code': req_code,
        'timestamp': timestamp,
        'files': files,
        'size': size,
        'duration': duration
    }

@bp.post('/upload')
@login_required
def upload():
    # create a new request
    req = create_req()
    return 'test'

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

@bp.route('/req/<req_code>', methods=['GET', 'POST'])
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
