import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///contentControl.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'f031e3f82adba6116acdbfa3a3fcddf2'
    