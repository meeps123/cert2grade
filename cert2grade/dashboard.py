import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from cert2grade.auth import login_required
from cert2grade.db import get_db

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    request_history = db.execute(
        'SELECT * FROM requests WHERE user_id = ?', (session['user_id'],)
    ).fetchall()
    return render_template('index.html', request_history=request_history)

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        raise Exception

@bp.route('/delete_request', methods=['POST'])
@login_required
def delete_request():
    request_codes = request.form['req_codes'].split('|')
    repl_str = '?,'*len(request_codes)
    repl_str = repl_str[:-1]
    query = 'DELETE FROM requests WHERE user_id = ? AND code IN (' + repl_str + ')'
    print(request_codes)
    print(query)
    success = True
    try:
        db = get_db()
        db.execute(query, (session['user_id'], *request_codes))
        print(db)
        db.commit()
    except:
        success = False
        flash('error deleting requests')
    return json.dumps({'success': success}), 200, {'ContentType': 'application/json'}