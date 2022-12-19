import json
import shortuuid
import os
from datetime import datetime
from threading import Lock
from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from markupsafe import escape
from pathlib import Path
from cert2grade.auth import login_required
from cert2grade.db import get_db

bp = Blueprint('dashboard', __name__)
lock = Lock()

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

@bp.post('/create_req')
@login_required
def create_req():
    user_id = session['user_id']
    req_code = shortuuid.ShortUUID().random(length=6)
    timestamp = datetime.now().timestamp()
    files = -1 # not sure of the number of files yet
    size = '' # not sure of the full size yet
    duration = -1 # hasn't started 
    query = 'INSERT INTO requests (user_id, code, timestamp, files, size, duration) VALUES (?, ?, ?, ?, ?, ?)'
    payload = {
        'success': True,
        'code': req_code
    }
    try:
        # create the entry in the db
        db = get_db()
        db.execute(query, (user_id, req_code, timestamp, files, size, duration))
        db.commit()

        # create the req's files folder, and the temp folder to store chunks
        req_folder = os.path.join(current_app.instance_path,'files', req_code)
        req_chunks_folder = os.path.join(req_folder, 'chunks')
        Path(req_chunks_folder).mkdir(parents=True, exist_ok=False)
    except:
        payload['success'] = False
    return json.dumps(payload), 200, {'ContentType': 'application/json'}

@bp.post('/upload/<req_code>')
@login_required
def upload(req_code):
    req_code = escape(req_code)

    file = request.files['file']
    if not file:
        abort(400) # no file provided
    dztotalchunkcount = int(request.form['dztotalchunkcount'])
    
    req_folder = os.path.join(current_app.instance_path,'files', req_code)
    req_chunks_folder = os.path.join(req_folder, 'chunks')
    filepath = os.path.join(req_folder, secure_filename(file.filename))

    # if file is small enough that it doesn't get chunked
    # we can just save it directly
    if dztotalchunkcount == 1:
        with open(filepath, 'wb') as f:
            file.save(f)
        return 'file_saved_successfully'

    # else, file is too big and will get chunked
    # we send the chunks to a temp dir in the req folder first
    chunk_save_dir = os.path.join(req_chunks_folder, request.form['dzuuid'])
    Path(chunk_save_dir).mkdir(parents=True, exist_ok=True)
    chunk_filepath = os.path.join(chunk_save_dir, request.form['dzchunkindex'])
    with open(chunk_filepath, 'wb') as f:
        file.save(f)

    # check if all chunks downloaded
    with lock:
        completed = len(os.listdir(chunk_save_dir)) == dztotalchunkcount
    
    # if all chunks downloaded, concat and save
    if completed:
        filepath = os.path.join()
        with open(filepath, 'ab') as f:
            for chunk_index in range(dztotalchunkcount):
                f.write((os.path.join(chunk_save_dir, chunk_index)).read_bytes())
        os.rmdir(chunk_save_dir)
    return 'chunk_file_upload_successful'

@bp.post('/delete_req')
@login_required
def delete_req():
    req_codes = request.form['req_codes'].split('|')
    repl_str = '?,'*len(req_codes)
    repl_str = repl_str[:-1]
    query = 'DELETE FROM requests WHERE user_id = ? AND code IN (' + repl_str + ')'
    success = True
    try:
        # delete the entries from the db
        db = get_db()
        db.execute(query, (session['user_id'], *req_codes))
        db.commit()
        affectedRows = db.execute('SELECT changes()').fetchone()[0]
        if affectedRows == 0: raise Exception
        
        # delete the entries from the filesystem
        for code in req_codes:
            print(req_codes)
            print(os.path.join(current_app.instance_path, 'files', code))
            os.rmdir(os.path.join(current_app.instance_path, 'files', code))
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
        # failed to fetch the req, either because
        # 1) the req code doesn't exist in the entire db
        # 2) the user's req don't have that code
        return render_template('404.html') 
    if req['duration'] > 0:
        # the req has completed
        files = db.execute(
            'SELECT * FROM files WHERE request_id = ?', (req['request_id'],)
        ).fetchall()
        return render_template('view_results.html', req_code=code, files=files)
    elif req['duration'] == -1:
        # in the churning phase
        return render_template('churn.html', req_code=code)