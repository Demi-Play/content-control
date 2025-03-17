import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'f031e3f82adba6116acdbfa3a3fcddf2'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///contentControl.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'application/static/uploads')
    
    # Настройки почты
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'd68350897@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'hgnt zlhj wyoi smio')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'Content Control <d68350897@gmail.com>')
    