from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, FileField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, equal_to

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    
class ResetPasswordForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Новый Пароль', validators=[DataRequired()])
    submit = SubmitField('Сбросить пароль')

class PostForm(FlaskForm):
    content_text = TextAreaField('Контент', validators=[DataRequired()])
    file = FileField('Загрузить файл')
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
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Роль', choices=[('user', 'Пользователь'), ('moderator', 'Модератор'), ('admin', 'Администратор')], validators=[DataRequired()])
    submit = SubmitField('Сохранить изменения')

class EventForm(FlaskForm):
    title = StringField('Название события', validators=[DataRequired()])
    description = TextAreaField('Описание события')
    date = DateTimeField('Дата события', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], render_kw={"type": "datetime-local"})
    submit = SubmitField('Добавить событие')

class NewsForm(FlaskForm):
    title = StringField('Название новости', validators=[DataRequired()])
    content = TextAreaField('Содержание новости', validators=[DataRequired()])
    submit = SubmitField('Добавить новость')