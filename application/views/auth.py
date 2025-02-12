from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import Post, db, User
from ..forms import RegistrationForm, LoginForm, ResetPasswordForm

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
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  # Сохраняем ID пользователя в сессии
            session['role'] = user.role  # Сохраняем Role пользователя в сессии
            flash('Login successful!')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем ID пользователя из сессии
    flash('You have been logged out.')
    return redirect(url_for('index'))

@auth_bp.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    user = User.query.get_or_404(user_id)
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
