from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import Post, db, User, UserActivity
from ..forms import RegistrationForm, LoginForm, ResetPasswordForm
import logging
from flask_login import login_user, logout_user, current_user, login_required
from ..app import login_manager
from datetime import datetime, timedelta
from ..utils.notifications import notify_user_blocked

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
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user:
            flash('Пользователь не найден', 'error')
            return render_template('auth/login.html', form=form)
            
        if not user.is_active:
            if user.is_blocked:
                flash('Ваш аккаунт заблокирован администратором', 'error')
                return render_template('auth/login.html', form=form)
                
            if user.blocked_until and user.blocked_until > datetime.now():
                remaining_time = (user.blocked_until - datetime.now()).seconds // 60
                flash(f'Ваш аккаунт временно заблокирован. Попробуйте через {remaining_time} минут', 'error')
                return render_template('login.html', form=form)
        
        if not user.check_password(form.password.data):
            user.failed_login_attempts += 1
            user.last_failed_login = datetime.now()
            
            if user.failed_login_attempts >= 3:
                user.blocked_until = datetime.now() + timedelta(minutes=15)
                # Отправляем уведомление о временной блокировке
                notify_user_blocked(user.id, 'temporary', duration=15, 
                                 reason='Превышено количество попыток входа')
                flash('Превышено количество попыток входа. Аккаунт заблокирован на 15 минут', 'error')
            else:
                remaining_attempts = 3 - user.failed_login_attempts
                flash(f'Неверный пароль. Осталось попыток: {remaining_attempts}', 'error')
                
            db.session.commit()
            return render_template('login.html', form=form)
            
        # Успешный вход
        user.failed_login_attempts = 0
        user.last_failed_login = None
        user.blocked_until = None
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        flash('Вы успешно вошли в систему!', 'success')
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        return redirect(next_page)
        
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
