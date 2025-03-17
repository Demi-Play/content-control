from flask import render_template
from flask_mail import Message
from ..models import db, Notification, User
from ..app import mail
import smtplib

def send_email_notification(user, subject, template, **kwargs):
    """Отправка email уведомления"""
    if not user.email_notifications:
        return
        
    msg = Message(
        subject,
        recipients=[user.email]
    )
    msg.html = render_template(template, user=user, **kwargs)
    mail.send(msg)

def create_system_notification(user_id, title, message):
    """Создание системного уведомления"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type='system'
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def create_moderation_notification(user_id, title, message):
    """Создание уведомления для модерации"""
    # Находим всех модераторов
    moderators = User.query.filter_by(role='moderator').all()
    
    # Создаем уведомление для каждого модератора
    for moderator in moderators:
        notification = Notification(
            user_id=moderator.id,
            title=title,
            message=message,
            type='moderation'
        )
        db.session.add(notification)
    
    db.session.commit()

def notify_post_moderation(post_id, status, reason=None):
    """Уведомление о результате модерации поста"""
    from ..models import Post
    
    post = Post.query.get(post_id)
    if not post:
        return
        
    title = "Результат модерации публикации"
    message = f"Ваша публикация была {'одобрена' if status == 'approved' else 'отклонена'}"
    if reason:
        message += f". Причина: {reason}"
    
    # Создаем системное уведомление
    create_system_notification(post.user_id, title, message)
    
    # Отправляем email
    user = User.query.get(post.user_id)
    if user and user.email_notifications:
        send_email_notification(
            user,
            title,
            'email/post_moderation.html',
            post=post,
            status=status,
            reason=reason
        )

def notify_new_comment(post_id, comment_id):
    """Уведомление о новом комментарии"""
    from ..models import Post, Comment
    
    comment = Comment.query.get(comment_id)
    post = Post.query.get(post_id)
    if not post or not comment:
        return
        
    # Уведомляем автора поста
    if post.user_id != comment.user_id:  # Не уведомляем, если автор комментирует свой пост
        title = "Новый комментарий к вашей публикации"
        message = f"Пользователь {comment.user.username} оставил комментарий к вашей публикации"
        
        create_system_notification(post.user_id, title, message)
        
        # Отправляем email
        user = User.query.get(post.user_id)
        if user and user.email_notifications:
            send_email_notification(
                user,
                title,
                'email/new_comment.html',
                post=post,
                comment=comment
            )

def notify_new_post_for_moderation(post_id):
    """Уведомление модераторов о новом посте для модерации"""
    from ..models import Post
    
    post = Post.query.get(post_id)
    if not post:
        return
        
    title = "Новая публикация для модерации"
    message = f"Пользователь {post.author.username} создал новую публикацию, требующую модерации"
    
    create_moderation_notification(None, title, message)

def test_email_configuration(app):
    """Тестирование конфигурации email"""
    from flask_mail import Message
    from ..app import mail
    
    with app.app_context():
        try:
            # Проверяем наличие всех необходимых настроек
            if not app.config.get('MAIL_USERNAME'):
                raise ValueError("MAIL_USERNAME not configured")
            if not app.config.get('MAIL_PASSWORD'):
                raise ValueError("MAIL_PASSWORD not configured")
                
            print(f"Testing email configuration...")
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            
            # Пробуем создать SMTP соединение напрямую для проверки
            smtp = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            smtp.ehlo()
            if app.config['MAIL_USE_TLS']:
                smtp.starttls()
            smtp.ehlo()
            
            # Пробуем аутентифицироваться
            smtp.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            print("SMTP authentication successful!")
            smtp.quit()
            
            # Если SMTP-аутентификация прошла успешно, пробуем отправить тестовое письмо
            msg = Message(
                "Test Email",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[app.config['MAIL_USERNAME']]
            )
            msg.body = "This is a test email to verify the configuration."
            mail.send(msg)
            print("Test email sent successfully!")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication Error: {str(e)}")
            print("Please check your email and password, and make sure you're using an App Password if 2FA is enabled.")
            return False
        except Exception as e:
            print(f"Error during email test: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return False

def notify_user_blocked(user_id, block_type, duration=None, reason=None):
    """
    Отправляет уведомление пользователю о блокировке
    :param user_id: ID пользователя
    :param block_type: Тип блокировки ('temporary' или 'permanent')
    :param duration: Продолжительность блокировки (для временной блокировки)
    :param reason: Причина блокировки
    """
    user = User.query.get(user_id)
    if not user or not user.email:
        return False
        
    # Формируем текст уведомления
    if block_type == 'temporary':
        subject = "Ваш аккаунт временно заблокирован"
        duration_text = f"на {duration} минут" if duration else ""
        body = f"Ваш аккаунт был временно заблокирован {duration_text}."
    else:
        subject = "Ваш аккаунт заблокирован"
        body = "Ваш аккаунт был заблокирован администратором."
        
    if reason:
        body += f"\n\nПричина: {reason}"
        
    body += "\n\nЕсли вы считаете, что это ошибка, пожалуйста, свяжитесь с администрацией."
    
    # Создаем и отправляем email
    msg = Message(
        subject,
        recipients=[user.email],
        body=body
    )
    
    try:
        mail.send(msg)
        
        # Создаем системное уведомление
        notification = Notification(
            user_id=user_id,
            title=subject,
            content=body,
            notification_type='system'
        )
        db.session.add(notification)
        db.session.commit()
        
        return True
    except Exception as e:
        print(f"Error sending block notification: {str(e)}")
        return False 