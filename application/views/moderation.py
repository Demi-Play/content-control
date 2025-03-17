from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from application.decorators import moderator_required
from ..models import Post, ModerationLog, db, UserActivity, News, Event, User, Notification
from datetime import datetime, timedelta
from ..utils.notifications import notify_post_moderation, create_system_notification

moderation_bp = Blueprint("moderation", __name__)

@moderation_bp.route("/moderate")
@login_required
@moderator_required('moderator')
def dashboard():
    # Получаем статистику за последние 7 дней
    last_week = datetime.now() - timedelta(days=7)
    
    # Статистика активности
    activities = UserActivity.query.filter(UserActivity.created_at >= last_week).order_by(UserActivity.created_at.desc()).all()
    
    # Статистика по типам контента
    posts_count = Post.query.count()
    news_count = News.query.count()
    events_count = Event.query.count()
    
    # Активные пользователи
    active_users = db.session.query(User, db.func.count(UserActivity.id).label('activity_count'))\
        .join(UserActivity)\
        .filter(UserActivity.created_at >= last_week)\
        .group_by(User.id)\
        .order_by(db.text('activity_count DESC'))\
        .limit(10)\
        .all()
    
    return render_template(
        "moderation/dashboard.html",
        activities=activities,
        posts_count=posts_count,
        news_count=news_count,
        events_count=events_count,
        active_users=active_users
    )

@moderation_bp.route("/moderate/posts")
@login_required
@moderator_required('moderator')
def moderate_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("moderation/moderate_posts.html", posts=posts)

@moderation_bp.route("/moderate/news")
@login_required
@moderator_required('moderator')
def moderate_news():
    news_items = News.query.order_by(News.created_at.desc()).all()
    return render_template("moderation/news.html", news_items=news_items)

@moderation_bp.route("/moderate/events")
@login_required
@moderator_required('moderator')
def moderate_events():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template("moderation/events.html", events=events)

@moderation_bp.route("/moderate/activities")
@login_required
@moderator_required('moderator')
def view_activities():
    # Фильтры
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type')
    target_type = request.args.get('target_type')
    days = request.args.get('days', type=int, default=7)
    
    query = UserActivity.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action_type:
        query = query.filter_by(action_type=action_type)
    if target_type:
        query = query.filter_by(target_type=target_type)
    if days:
        query = query.filter(UserActivity.created_at >= datetime.now() - timedelta(days=days))
    
    activities = query.order_by(UserActivity.created_at.desc()).all()
    users = User.query.all()
    
    return render_template(
        "moderation/activities.html",
        activities=activities,
        users=users,
        selected_user_id=user_id,
        selected_action_type=action_type,
        selected_target_type=target_type,
        selected_days=days
    )

@moderation_bp.route("/approve/<int:post_id>", methods=["POST"])
@login_required
@moderator_required('moderator')
def approve_post(post_id):
    post = Post.query.get_or_404(post_id)
    log_entry = ModerationLog(post_id=post.id, status="approved")
    post.is_active = True
    
    # Логируем действие модератора
    activity = UserActivity(
        user_id=current_user.id,
        action_type='approve',
        target_type='post',
        target_id=post.id,
        details='Post approved by moderator'
    )
    
    db.session.add(log_entry)
    db.session.add(activity)
    
    # Отправляем уведомление автору поста
    notify_post_moderation(post.id, 'approved')
    
    db.session.commit()
    
    flash(f"Пост {post.id} одобрен!", 'success')
    return redirect(url_for("moderation.moderate_posts"))

@moderation_bp.route("/reject/<int:post_id>", methods=["POST"])
@login_required
@moderator_required('moderator')
def reject_post(post_id):
    post = Post.query.get_or_404(post_id)
    reason = request.form.get('reason', '')  # Получаем причину отклонения, если она есть
    
    log_entry = ModerationLog(post_id=post.id, status="rejected", reason=reason)
    post.is_active = False
    
    # Логируем действие модератора
    activity = UserActivity(
        user_id=current_user.id,
        action_type='reject',
        target_type='post',
        target_id=post.id,
        details='Post rejected by moderator'
    )
    
    db.session.add(log_entry)
    db.session.add(activity)
    
    # Отправляем уведомление автору поста с причиной отклонения
    notify_post_moderation(post.id, 'rejected', reason)
    
    db.session.commit()
    
    flash(f"Пост {post.id} отклонен!", 'error')
    return redirect(url_for("moderation.moderate_posts")) 