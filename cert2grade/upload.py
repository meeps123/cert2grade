import os
import shutil
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

bp = Blueprint('upload', __name__)
lock = Lock()
chunks = defaultdict(list)

@bp.post('/upload/<req_code>')
@login_required
def upload(req_code):
    db = get_db()

    # get the req code
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
    filename = secure_filename(file.filename)
    filepath = os.path.join(req_folder, filename)
    query = 'INSERT INTO files (request_id, filename, size, has_thumbnail) VALUES (?, ?, ?, ?)'

    # if file is small enough that it doesn't get chunked
    # we can just save it directly and add to db
    if dztotalchunkcount == 1:
        with open(filepath, 'wb') as f:
            file.save(f)
        db.execute(query, (request_id, filename, int(request.form['dztotalfilesize']), 0))
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
        db.execute(query, (request_id, filename, int(request.form['dztotalfilesize']), 0))
        db.commit()
    return 'chunk_file_upload_successful'

@bp.post('/upload_thumbnail/<req_code>')
@login_required
def upload_thumbnail(req_code):
    db = get_db()
    
    # get the req code
    req_code = escape(req_code)

    print(req_code)
    print(request)
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
    