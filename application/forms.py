from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, FileField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, equal_to, ValidationError
from flask_wtf.file import FileAllowed
from application.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, message='Пароль должен содержать минимум 6 символов')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    
class ResetPasswordForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(message='Пожалуйста, введите имя пользователя')])
    email = StringField('Email', validators=[
        DataRequired(message='Пожалуйста, введите email'),
        Email(message='Пожалуйста, введите корректный email')
    ])
    password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Пожалуйста, введите новый пароль'),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    password2 = PasswordField('Повторите пароль', validators=[
        DataRequired(message='Пожалуйста, повторите пароль'),
        equal_to('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Сбросить пароль')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('Пользователь с таким именем не найден')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Пользователь с таким email не найден')
        
        # Проверяем, что email соответствует указанному пользователю
        username_user = User.query.filter_by(username=self.username.data).first()
        if username_user and username_user.email != email.data:
            raise ValidationError('Email не соответствует указанному пользователю')

class PostForm(FlaskForm):
    content_text = TextAreaField('Контент', validators=[DataRequired()])
    file = FileField('Загрузить файл', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm', 'mp3', 'wav'], 'Разрешены только изображения, видео и аудио файлы!')
    ])
    submit = SubmitField('Отправить')

class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')

class ModerationForm(FlaskForm):
    status = SelectField('Статус', choices=[('approved', 'Approve'), ('rejected', 'Reject')], validators=[DataRequired()])
    submit = SubmitField('Обновить статус')
    
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

class UserEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'),
        Length(min=2, max=150, message='Имя пользователя должно быть от 2 до 150 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email')
    ])
    role = SelectField('Роль', choices=[
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор')
    ], validators=[DataRequired(message='Выберите роль')])
    password = PasswordField('Новый пароль')
    submit = SubmitField('Сохранить изменения')

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        if 'obj' in kwargs:
            self.obj = kwargs['obj']

    def validate_password(self, field):
        if field.data and len(field.data) < 6:
            raise ValidationError('Пароль должен содержать минимум 6 символов')

class EventForm(FlaskForm):
    title = StringField('Название события', validators=[DataRequired()])
    description = TextAreaField('Описание события')
    date = DateTimeField('Дата события', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], render_kw={"type": "datetime-local"})
    submit = SubmitField('Добавить событие')

class NewsForm(FlaskForm):
    title = StringField('Название новости', validators=[DataRequired()])
    content = TextAreaField('Содержание новости', validators=[DataRequired()])
    submit = SubmitField('Добавить новость')