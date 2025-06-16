# run.py

from application.app import app
from application.models import db

if __name__ == '__main__':
    with app.app_context():
        # Создание базы данных и таблиц (если еще не созданы)
        db.create_all()
    app.run(debug=True)
