import os
from flask import Flask, render_template
from .config import Config
from .models import db, Event, News
from transliterate import translit
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config.from_object(Config)

def transliterate_filename(filename):
    # Удаляем пробелы и расширение
    name, ext = os.path.splitext(filename)
    # Транслитерируем имя файла
    transliterated_name = translit(name, 'ru', reversed=True)
    # Формируем новое имя файла
    new_filename = f"{transliterated_name}.{ext}"
    return new_filename

# Инициализация базы данных
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)

# Создание базы данных и таблиц (если еще не созданы)
with app.app_context():
    db.create_all()

# Импортировать views после инициализации приложения
from .views.auth import auth_bp
from .views.posts import posts_bp
from .views.likes import likes_bp
from .views.comments import comments_bp
from .views.moderation import moderation_bp
from .views.admin import admin_bp
from .views.events import events_bp
from .views.news import news_bp

# Регистрация блюпринтов (blueprints)
app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(likes_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(moderation_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(events_bp)
app.register_blueprint(news_bp)

@app.route('/')
def index():
    events = Event.query.order_by(Event.date.desc()).limit(3).all()
    news_items = News.query.order_by(News.created_at.desc()).limit(3).all()
    return render_template('index.html', events=events, news_items=news_items)

if __name__ == '__main__':
    app.run(debug=True)