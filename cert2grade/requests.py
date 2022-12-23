import json
import shortuuid
import os
import shutil
from datetime import datetime
from flask import (
    Blueprint, current_app, request, session
)
from werkzeug.exceptions import abort
from markupsafe import escape
from pathlib import Path
from cert2grade.auth import login_required
from cert2grade.db import get_db

bp = Blueprint('requests', __name__)

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

@bp.post('/delete_req')
@login_required
def delete_req():
    req_codes = request.form['req_codes'].split('|')
    success = True
    try:
        db = get_db()
        db.execute('PRAGMA FOREIGN_KEYS = ON') # enable ON DELETE CASCADE behavior

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

        # Due to ON DELETE CASCADE it will auto-delete the files entries

        # delete the entire request folder from the filesystem
        for code in req_codes:
            shutil.rmtree(os.path.join(current_app.instance_path, 'files', code))
    except Exception as e:
        print(e)
        success = False
    return json.dumps({'success': success}), 200, {'ContentType': 'application/json'}

@bp.post('/update_req')
@login_required
def update_req():
    req_code = escape(request.form['req_code'])
    modifications = json.loads(request.form['modifications'])

    # check the keys of the pending modifications
    # simultaneously build the query
    allowed_keys = ['start_timestamp', 'files', 'size', 'end_timestamp']
    query = 'UPDATE requests SET '    
    for k in modifications.keys():
        if k in allowed_keys:
            query += f"{k} = {modifications[k]}, "
        else:
            abort(400)
    query = query[:-2] + f" WHERE code = \"{req_code}\""

    print(query)

    db = get_db()
    db.execute(query)
    db.commit()
    
    return 'records updated'