from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import Event, db, UserActivity
from ..forms import EventForm
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
def list_events():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('events.html', events=events)

@events_bp.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data
        )
        
        db.session.add(event)
        db.session.flush()  # Получаем id до коммита
        
        # Логируем действие
        activity = UserActivity(
            user_id=current_user.id,
            action_type='create',
            target_type='event',
            target_id=event.id,
            details=f'Created new event: {event.title}'
        )
        
        db.session.add(activity)
        db.session.commit()
        
        flash('Мероприятие успешно добавлено!', 'success')
        return redirect(url_for('events.list_events'))
    return render_template('add_event.html', form=form)

@events_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        
        # Логируем действие
        activity = UserActivity(
            user_id=current_user.id,
            action_type='edit',
            target_type='event',
            target_id=event_id,
            details=f'Edited event: {event.title}'
        )
        
        db.session.add(activity)
        db.session.commit()
        
        flash('Мероприятие успешно обновлено!', 'success')
        return redirect(url_for('events.list_events'))
    
    return render_template('edit_event.html', form=form, event=event)

@events_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Логируем действие перед удалением
    activity = UserActivity(
        user_id=current_user.id,
        action_type='delete',
        target_type='event',
        target_id=event_id,
        details=f'Deleted event: {event.title}'
    )
    
    db.session.add(activity)
    db.session.delete(event)
    db.session.commit()
    
    flash('Мероприятие успешно удалено!', 'success')
    return redirect(url_for('events.list_events')) 
