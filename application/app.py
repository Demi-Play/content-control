from flask import Flask, render_template
from .config import Config
from .models import db

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
db.init_app(app)

# Создание базы данных и таблиц (если еще не созданы)
with app.app_context():
    db.create_all()

# Импортировать views после инициализации приложения
from .views.auth import auth_bp
from .views.posts import posts_bp
from .views.comments import comments_bp
from .views.moderation import moderation_bp

# Регистрация блюпринтов (blueprints)
app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(moderation_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)