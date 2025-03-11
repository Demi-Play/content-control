from functools import wraps
from flask import session, redirect, url_for, flash
from flask_login import current_user

def moderator_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Пожалуйста, войдите в систему.', 'error')
                return redirect(url_for('auth.login'))
            if current_user.role != role:
                flash('У вас нет доступа к этой странице.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator