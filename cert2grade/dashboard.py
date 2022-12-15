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