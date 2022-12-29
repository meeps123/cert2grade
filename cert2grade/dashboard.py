import math
from datetime import datetime
from flask import (
    Blueprint, render_template, session
)
from markupsafe import escape
from cert2grade.auth import login_required
from cert2grade.db import get_db

bp = Blueprint('dashboard', __name__)

def convert_size(size_bytes):
    if size_bytes == 0:
        return '0B'
    size_name = ['B', 'KB', 'MB', 'GB', 'TB']
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes/p, 2)
    return f"{s} {size_name[i]}"

@bp.route('/')
@login_required
def index():
    db = get_db()
    req_history = db.execute(
        'SELECT * FROM requests WHERE user_id = ? ORDER BY start_timestamp DESC', (session['user_id'],)
    ).fetchall()
    json_req_history = [dict((req.keys()[k],v) for k,v in enumerate(req)) for req in req_history]
    for req in json_req_history:
        # format the duration which the user sees
        start_timestamp = datetime.fromtimestamp(req['start_timestamp'])
        if req['end_timestamp'] == -1:
            req['duration'] = 'awaiting user input'
        elif req['end_timestamp'] == 0:
            req['duration'] = 'in progress'
        else:
            end_timestamp = datetime.fromtimestamp(req['end_timestamp'])
            req['duration'] = f"{(end_timestamp - start_timestamp).total_seconds()}s"
        
        # format the timestamp which the user sees
        req['timestamp'] = start_timestamp.strftime('%d-%m-%Y %H:%M:%S')

        # format the size string which the user sees
        size_str = f"{req['files']} file{'' if req['files'] == 1 else 's'}"
        size_str += f" ({convert_size(req['size'])})"
        req['size_str'] = size_str

    return render_template('index.html', req_history=json_req_history)

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
        for file in files:
            existing_files.append({
                'name': file['filename'],
                'size': file['size'],
                'accepted': True,
                'processing': True,
                'status': 'success',
                'upload': {
                    'progress': 100
                }
            })
        print(existing_files)
        return render_template('upload.html', req_code=code, existing_files=existing_files)
    elif req['end_timestamp'] == 0:
        # in the churning phase
        return render_template('churn.html', req_code=code, files=files)