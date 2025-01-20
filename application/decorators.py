from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Вы должны быть авторизованы для доступа к этой странице.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                flash("У вас нет доступа к этой странице.")
                return redirect(url_for('index')) 
            return f(*args, **kwargs)
        return decorated_function
    return decorator