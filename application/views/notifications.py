from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from ..models import db, Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
@login_required
def list_notifications():
    """Список уведомлений пользователя"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications/list.html', notifications=notifications)

@notifications_bp.route('/notifications/unread')
@login_required
def get_unread_count():
    """Получение количества непрочитанных уведомлений"""
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'count': count})

@notifications_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_as_read():
    """Отметить уведомления как прочитанные"""
    notification_ids = request.json.get('notification_ids', [])
    
    if notification_ids:
        Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user.id
        ).update({Notification.is_read: True}, synchronize_session=False)
    else:
        # Если ID не указаны, отмечаем все как прочитанные
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({Notification.is_read: True}, synchronize_session=False)
    
    db.session.commit()
    return jsonify({'success': True})

@notifications_bp.route('/notifications/settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    """Настройки уведомлений"""
    if request.method == 'POST':
        current_user.email_notifications = request.form.get('email_notifications') == 'on'
        db.session.commit()
        return jsonify({'success': True})
    
    return render_template('notifications/settings.html') 