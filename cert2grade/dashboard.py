import json
import shortuuid
import os
import shutil
from collections import defaultdict
from datetime import datetime
from threading import Lock
from flask import (
    Blueprint, current_app, render_template, request, session, jsonify
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from markupsafe import escape
from pathlib import Path
from cert2grade.auth import login_required
from cert2grade.db import get_db

bp = Blueprint('dashboard', __name__)
lock = Lock()
chunks = defaultdict(list)

@bp.route('/')
@login_required
def index():
    db = get_db()
    req_history = db.execute(
        'SELECT * FROM requests WHERE user_id = ? ORDER BY start_timestamp DESC', (session['user_id'],)
    ).fetchall()
    json_req_history = [dict((req.keys()[k],v) for k,v in enumerate(req)) for req in req_history]
    for req in json_req_history:
        start_timestamp = datetime.fromtimestamp(req['start_timestamp'])
        if req['end_timestamp'] == -1:
            req['duration'] = 'awaiting user input'
        elif req['end_timestamp'] == 0:
            req['duration'] = 'in progress'
        else:
            end_timestamp = datetime.fromtimestamp(req['end_timestamp'])
            req['duration'] = f"{(end_timestamp - start_timestamp).total_seconds()}s"
        req['timestamp'] = start_timestamp.strftime('%d-%m-%Y %H:%M:%S')

    return render_template('index.html', req_history=json_req_history)

@bp.post('/create_req')
@login_required
def create_req():
    user_id = session['user_id']
    req_code = shortuuid.ShortUUID().random(length=6)
    timestamp = datetime.now().timestamp()
    files = -1 # not sure of the number of files yet
    size = '' # not sure of the full size yet
    end_timestamp = -1 # hasn't started 
    query = 'INSERT INTO requests (user_id, code, start_timestamp, files, size, end_timestamp) VALUES (?, ?, ?, ?, ?, ?)'
    payload = {
        'success': True,
        'code': req_code
    }
    try:
        # create the entry in the db
        db = get_db()
        db.execute(query, (user_id, req_code, timestamp, files, size, end_timestamp))
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
    db = get_db()

    # get the request code from the variable route
    req_code = escape(req_code)

    # get the request id for the code
    try:
        request_id = db.execute(
            'SELECT * FROM requests WHERE user_id = ? AND code = ?',
            (session['user_id'], req_code)
        ).fetchone()['request_id']
    except:
        # failed to get the request id
        abort(404)

    file = request.files['file']
    if not file:
        abort(400) # no file provided
    dztotalchunkcount = int(request.form['dztotalchunkcount'])
    
    req_folder = os.path.join(current_app.instance_path,'files', req_code)
    req_chunks_folder = os.path.join(req_folder, 'chunks')
    filepath = os.path.join(req_folder, secure_filename(file.filename))
    query = 'INSERT INTO files (request_id, filepath, size) VALUES (?, ?, ?)'

    # if file is small enough that it doesn't get chunked
    # we can just save it directly and add to db
    if dztotalchunkcount == 1:
        with open(filepath, 'wb') as f:
            file.save(f)
        db.execute(query, (request_id, filepath, int(request.form['dztotalfilesize'])))
        db.commit()
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
        chunks[request.form['dzuuid']].append(int(request.form['dzchunkindex']))
        completed = len(chunks[request.form['dzuuid']]) == dztotalchunkcount
        # if all chunks downloaded, concat and save, add to db as well
    if completed:
        with open(filepath, 'ab') as f:
            for chunk_index in range(dztotalchunkcount):
                curr_chunkpath = os.path.join(chunk_save_dir, str(chunk_index))
                with open(curr_chunkpath, 'rb') as c: 
                    f.write(c.read())
            shutil.rmtree(chunk_save_dir)
        del chunks[request.form['dzuuid']]
        db.execute(query, (request_id, filepath, int(request.form['dztotalfilesize'])))
        db.commit()
    return 'chunk_file_upload_successful'

@bp.post('/delete_req')
@login_required
def delete_req():
    req_codes = request.form['req_codes'].split('|')
    success = True
    try:
        db = get_db()
        
        # delete the request entry from the db
        delete_req_query = 'DELETE FROM requests WHERE user_id = ? AND code = ?'
        request_ids = []
        for req_code in req_codes:
            # first get the target request id
            request_ids.append(
                db.execute(
                    'SELECT * FROM requests WHERE user_id = ? AND code = ?',
                    (session['user_id'], req_code)
                ).fetchone()['request_id']
            )
            # then delete the request
            db.execute(delete_req_query, (session['user_id'], req_code))
            db.commit()
            affectedRows = db.execute('SELECT changes()').fetchone()[0]
            if affectedRows == 0: raise Exception
        
        # delete the corresponding files entries from the db
        delete_file_query = 'DELETE FROM files WHERE request_id = ?'
        for request_id in request_ids:
            db.execute(delete_file_query, (request_id,))
            db.commit()
            affectedRows = db.execute('SELECT changes()').fetchone()[0]
            if affectedRows == 0: raise Exception

        # delete the entire request folder from the filesystem
        for code in req_codes:
            shutil.rmtree(os.path.join(current_app.instance_path, 'files', code))
    except:
        success = False
    return json.dumps({'success': success}), 200, {'ContentType': 'application/json'}

@bp.route('/req/<req_code>', methods=['GET', 'POST'])
@login_required
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
    files = db.execute(
        'SELECT * FROM files WHERE request_id = ?', (req['request_id'],)
    ).fetchall()
    if req['end_timestamp'] > 0:
        # the req has completed
        return render_template('view_results.html', req_code=code, files=files)
    elif req['end_timestamp'] == -1:
        # in the pre-churn phase
        existing_files = []
        # existing_blobs = []
        for file in files:
            existing_files.append({
                'name': file['filepath'].split('\\')[-1],
                'size': file['size'],
            })
            # existing_blobs.append(file['preview'])
        print(existing_files)
        # print(existing_blobs)
        return render_template('upload.html', req_code=code, existing_files=existing_files)
    elif req['end_timestamp'] == 0:
        # in the churning phase
        return render_template('churn.html', req_code=code, files=files)