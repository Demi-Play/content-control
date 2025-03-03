from flask import Blueprint, render_template, redirect, url_for, flash
from ..models import Event, db
from ..forms import EventForm
from application.decorators import login_required


events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
@login_required
def list_events():
    events = Event.query.all()
    return render_template('events.html', events=events)

@events_bp.route('/events/new', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    if form.validate_on_submit():
        print("Form data received:", form.data)  # Debug print
        event = Event(title=form.title.data, description=form.description.data, date=form.date.data)
        db.session.add(event)
        db.session.commit()
        flash('Event added successfully!')
        return redirect(url_for('events.list_events'))
    else:
        print("Form validation errors:", form.errors)  # Debug print
    return render_template('add_event.html', form=form)

@events_bp.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        db.session.commit()
        flash('Event updated successfully!')
        return redirect(url_for('events.list_events'))
    return render_template('edit_event.html', form=form, event=event)

@events_bp.route('/events/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!')
    return redirect(url_for('events.list_events')) 