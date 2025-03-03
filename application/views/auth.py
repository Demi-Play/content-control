from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import Post, db, User
from ..forms import RegistrationForm, LoginForm, ResetPasswordForm
import logging
from flask_login import login_user, logout_user, current_user
from ..app import login_manager

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
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.')
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log successful registration
        logger.info(f"User {username} registered successfully.")
        
        # Log in the user after registration
        login_user(new_user)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('auth.login'))
    
    # Log validation errors
    logger.error(f"Validation errors: {form.errors}")
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # Log in the user
            flash('Login successful!')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()  # Log out the user
    flash('You have been logged out.')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET'])
def profile():
    user = User.query.get_or_404(current_user.id)
    posts = Post.query.filter_by(user_id=user.id).all()  # Получаем все посты пользователя
    return render_template('profile.html', user=user, posts=posts)

@auth_bp.route('/forget_pass', methods=['GET', 'POST'])
def forget_pass():
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, email=form.email.data).first()
        
        if user:
            try:
                new_hashed_password = generate_password_hash(form.password.data)
                user.password_hash = new_hashed_password
                
                db.session.commit()
                
                flash("Пароль успешно изменён.", "success")
                return redirect(url_for("login"))
            
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при изменении пароля: {e}", "danger")
        
        else:
            flash('Некорректные данные пользователя', 'danger')
    
    return render_template('forget_pass.html', form=form)
