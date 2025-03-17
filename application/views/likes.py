from flask import Blueprint, redirect, url_for, flash
from flask_login import current_user, login_required
from ..models import db, Like, UserActivity

likes_bp = Blueprint('likes', __name__)

@likes_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    if current_user.is_anonymous:
        flash("Вы должны быть авторизованы для того, чтобы ставить лайки.")
        return redirect(url_for('auth.login'))

    existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()

    if existing_like:
        # Логируем удаление лайка
        activity = UserActivity(
            user_id=current_user.id,
            action_type='delete',
            target_type='like',
            target_id=post_id,
            details=f'Removed like from post {post_id}'
        )
        db.session.add(activity)
        db.session.delete(existing_like)
        db.session.commit()
        flash("Лайк убран!")
    else:
        new_like = Like(post_id=post_id, user_id=current_user.id)
        # Логируем добавление лайка
        activity = UserActivity(
            user_id=current_user.id,
            action_type='create',
            target_type='like',
            target_id=post_id,
            details=f'Added like to post {post_id}'
        )
        db.session.add(new_like)
        db.session.add(activity)
        db.session.commit()
        flash("Лайк поставлен!")

    return redirect(url_for('posts.list_posts'))

@likes_bp.route('/unlike/<int:post_id>', methods=['POST'])
def unlike_post(post_id):
    if current_user.is_anonymous:
        flash("Вы должны быть авторизованы для того, чтобы убрать лайк.")
        return redirect(url_for('auth.login'))

    existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()

    if existing_like:
        # Логируем удаление лайка
        activity = UserActivity(
            user_id=current_user.id,
            action_type='delete',
            target_type='like',
            target_id=post_id,
            details=f'Removed like from post {post_id}'
        )
        db.session.add(activity)
        db.session.delete(existing_like)
        db.session.commit()
        flash("Лайк убран!")
    else:
        flash("Вы не ставили лайк на этот пост.")

    return redirect(url_for('posts.list_posts'))