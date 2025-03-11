from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import Post, db, User
from ..forms import RegistrationForm, LoginForm, ResetPasswordForm
import logging
from flask_login import login_user, logout_user, current_user, login_required
from ..app import login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Проверяем существование пользователя
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует.', 'error')
            return redirect(url_for('auth.register'))
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Этот email уже зарегистрирован.', 'error')
            return redirect(url_for('auth.register'))
        
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Log successful registration
            logger.info(f"User {username} registered successfully.")
            
            # Log in the user after registration
            login_user(new_user)
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during registration: {str(e)}")
            flash('Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.', 'error')
            return redirect(url_for('auth.register'))
    
    # Log validation errors
    if form.errors:
        logger.error(f"Validation errors: {form.errors}")
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash('Пользователь с таким именем не найден.', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active():
            if user.is_blocked:
                flash('Ваш аккаунт заблокирован администратором.', 'error')
            else:
                remaining_time = 300 - (datetime.now() - user.last_failed_login).total_seconds()
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                flash(f'Слишком много неудачных попыток входа. Попробуйте через {minutes} мин. {seconds} сек.', 'error')
            return redirect(url_for('auth.login'))
            
        if not check_password_hash(user.password_hash, password):
            user.increment_failed_login()
            if user.failed_login_attempts >= 3:
                flash('Слишком много неудачных попыток входа. Попробуйте через 5 минут.', 'error')
            else:
                flash('Неверный пароль.', 'error')
            return redirect(url_for('auth.login'))
        
        # Сбрасываем счетчик неудачных попыток при успешном входе
        user.reset_failed_login()
        login_user(user)
        flash('Вход выполнен успешно!', 'success')
        return redirect(url_for('index'))
    
    if form.errors:
        logger.error(f"Login form validation errors: {form.errors}")
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы.', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(current_user.id)
    posts = Post.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, posts=posts)

@auth_bp.route('/forget_pass', methods=['GET', 'POST'])
def forget_pass():
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data, email=form.email.data).first()
            
            if not user:
                flash('Пользователь с указанными данными не найден.', 'error')
                return redirect(url_for('auth.forget_pass'))
            
            # Проверяем, что новый пароль отличается от текущего
            if check_password_hash(user.password_hash, form.password.data):
                flash('Новый пароль не должен совпадать с текущим.', 'error')
                return redirect(url_for('auth.forget_pass'))
            
            new_hashed_password = generate_password_hash(form.password.data)
            user.password_hash = new_hashed_password
            
            db.session.commit()
            
            # Логируем успешное изменение пароля
            logger.info(f"Password reset successful for user: {user.username}")
            
            flash('Пароль успешно изменён. Теперь вы можете войти с новым паролем.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during password reset: {str(e)}")
            flash('Произошла ошибка при изменении пароля. Пожалуйста, попробуйте позже.', 'error')
    
    if form.errors:
        logger.error(f"Password reset form validation errors: {form.errors}")
    
    return render_template('forget_pass.html', form=form)
