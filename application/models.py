from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128), default='user')
    is_blocked = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    email_notifications = db.Column(db.Boolean, default=True)  # Флаг для email уведомлений
    
    # is_blocked = db.Column(db.Boolean, default=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_active(self):
        # First check if user is blocked
        if self.is_blocked:
            return False
            
        # Then check for temporary block due to failed login attempts
        if self.failed_login_attempts >= 3:
            if self.last_failed_login and (datetime.now() - self.last_failed_login).total_seconds() < 300:  # 5 минут
                return False
            else:
                # Reset counter after 5 minutes
                self.failed_login_attempts = 0
                return True
        return True

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.now()
        db.session.commit()

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.last_failed_login = None
        db.session.commit()

    def __repr__(self):
        return f"<User {self.username}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_text = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(10), nullable=False)  # 'image', 'video', or 'none'
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = db.Column(db.Boolean, default=True)

    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)

    def __repr__(self):
        return f"<Post {self.id}, User {self.user_id}>"

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Like Post {self.post_id}, User {self.user_id}>"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Comment Post {self.post_id}, User {self.user_id}>"

class ModerationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Статус проверки (например: 'approved', 'rejected')
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<ModerationLog Post {self.post_id}, Status {self.status}>"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Event {self.title}>"

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<News {self.title}>"

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # 'create', 'edit', 'delete'
    target_type = db.Column(db.String(50), nullable=False)  # 'post', 'comment', 'news', 'event'
    target_id = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='activities')

    def __repr__(self):
        return f"<UserActivity {self.user_id} {self.action_type} {self.target_type} {self.target_id}>"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'system', 'moderation', 'email'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f"<Notification {self.id} for User {self.user_id}>"
