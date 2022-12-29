import os
import shutil
import json
import base64
from collections import defaultdict
from threading import Lock
from flask import (
    Blueprint, current_app, request, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from markupsafe import escape
from pathlib import Path
from cert2grade.auth import login_required
from cert2grade.db import get_db

bp = Blueprint('file', __name__)
lock = Lock()
chunks = defaultdict(list)

@bp.post('/upload_file/<req_code>')
@login_required
def upload_file(req_code):
    db = get_db()

    # get the req code
    req_code = escape(req_code)

    # get the request id for the code
    try:
        req_id = db.execute(
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
    filename = secure_filename(file.filename)
    filepath = os.path.join(req_folder, filename)
    query = 'INSERT INTO files (request_id, filename, size, has_thumbnail) VALUES (?, ?, ?, ?)'

    # if file is small enough that it doesn't get chunked
    # we can just save it directly and add to db
    if dztotalchunkcount == 1:
        with open(filepath, 'wb') as f:
            file.save(f)
        db.execute(query, (req_id, filename, int(request.form['dztotalfilesize']), 0))
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
        db.execute(query, (req_id, filename, int(request.form['dztotalfilesize']), 0))
        db.commit()
    return 'chunk_file_upload_successful'

@bp.post('/delete_file/')
@login_required
def delete_file():
    db = get_db()
    
    # get the JSON data that was sent over
    req_code = request.form['req_code']
    filenames = json.loads(request.form['filenames'])

    success = True

    # get the request id for the code
    try:
        req_id = db.execute(
            'SELECT * FROM requests WHERE user_id = ? AND code = ?',
            (session['user_id'], req_code)
        ).fetchone()['request_id']
    except:
        # failed to get the request id
        abort(400)
    
    # form the delete query
    delete_file_query = 'DELETE FROM files WHERE request_id = ? AND filename IN ('
    delete_file_query = delete_file_query + '?, ' * len(filenames)
    delete_file_query = f"{delete_file_query[:-2]})"

    # execute the delete query
    try:
        db.execute(delete_file_query, (req_id, *filenames))
        db.commit()
        affectedRows = db.execute('SELECT changes()').fetchone()[0]
        if affectedRows == 0: raise Exception
    except Exception as e:
        print(delete_file_query)
        print(e)
        success = False
        return json.dumps({'success': success}), 200, {'ContentType': 'application/json'}

    # execute the filesystem delete
    try:
        for filename in filenames:
            filepath = os.path.join(current_app.instance_path, 'files', req_code, filename)
            thumbnail_filename = f"{filename.split('.')[0]}_thumbnail.png"
            thumbnail_path = os.path.join(current_app.instance_path, 'files', req_code, thumbnail_filename)
            os.remove(filepath)
            os.remove(thumbnail_path)
    except Exception as e:
        print(e)
        success = False

    return json.dumps({'success': success}), 200, {'ContentType': 'application/json'}

@bp.post('/upload_thumbnail/<req_code>')
@login_required
def upload_thumbnail(req_code):
    db = get_db()
    
    # get the req code
    req_code = escape(req_code)

    # get the thumbnail
    thumbnail = request.files['file']
    if not thumbnail:
        abort(400) # no thumbnail provided

    # save the thumbnail
    thumbnail_path = os.path.join(
        current_app.instance_path, 
        'files', 
        req_code, 
        secure_filename(thumbnail.filename)
    )
    with open(thumbnail_path, 'wb') as f:
        thumbnail.save(f)

    # update the db to indicate that the thumbnail is present
    corr_filename = secure_filename(thumbnail.filename).split('_thumbnail.png')[0] + '.pdf'
    query = 'UPDATE files SET has_thumbnail = 1 WHERE filename = ?'
    db.execute(query, (corr_filename,))
    db.commit()

    return 'thumbnail saved successfully'
    
@bp.post('/download_thumbnail')
@login_required
def download_thumbnail():
    db = get_db()

    # get the data that was sent over
    req_code = request.form['req_code']
    filename = request.form['filename']

    # get the request id for the code
    try:
        req_id = db.execute(
            'SELECT * FROM requests WHERE user_id = ? AND code = ?',
            (session['user_id'], req_code)
        ).fetchone()['request_id']
    except:
        # failed to get the request id
        abort(404)

    # attempt to read the thumbnail for the specified filename
    thumbnail_filename = secure_filename(f"{filename.split('.')[0]}_thumbnail.png")
    thumbnail_filepath = os.path.join(current_app.instance_path, 'files', req_code, thumbnail_filename)

    success = True
    data_url = 'data:image/png;base64,'
    try:
        with open(thumbnail_filepath, 'rb') as f:
            thumbnail_data = f.read()
            data_url += base64.b64encode(thumbnail_data).decode()
    except Exception as e:
        print(thumbnail_filepath)
        print(e)
        success = False
    
    payload = {
        'success': success,
        'data_url': data_url
    }
    return json.dumps(payload), 200, {'ContentType': 'application/json'}
