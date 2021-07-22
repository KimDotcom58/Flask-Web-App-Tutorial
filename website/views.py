from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from .extensions import db
import json
from .extensions import scheduler
from .tasks import task2

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

@views.route("/add")
def add():
    """Add a task.

    :url: /add/
    :returns: job
    """
    job = scheduler.add_job(
        func=task2,
        trigger="interval",
        seconds=10,
        id="test job 2",
        name="test job 2",
        replace_existing=True,
    )
    return "%s added!" % job.name

@views.route("/remove")
def remove():
    """Remove a task.

    :url: /remove/
    :returns: job
    """
    scheduler.remove_job(
        id="test job 2"
    )
    return "Removed!"

