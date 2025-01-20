from flask import Blueprint, session, redirect, url_for, flash

from application.decorators import login_required
from ..models import db, Like

likes_bp = Blueprint('likes', __name__)

@likes_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    if 'user_id' not in session:
        flash("Вы должны быть авторизованы для того, чтобы ставить лайки.")
        return redirect(url_for('auth.login'))

    existing_like = Like.query.filter_by(post_id=post_id, user_id=session['user_id']).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        flash("Лайк убран!")
    else:
        new_like = Like(post_id=post_id, user_id=session['user_id'])
        db.session.add(new_like)
        db.session.commit()
        flash("Лайк поставлен!")

    return redirect(url_for('posts.list_posts'))

@likes_bp.route('/unlike/<int:post_id>', methods=['POST'])
def unlike_post(post_id):
    if 'user_id' not in session:
        flash("Вы должны быть авторизованы для того, чтобы убрать лайк.")
        return redirect(url_for('auth.login'))

    existing_like = Like.query.filter_by(post_id=post_id, user_id=session['user_id']).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        flash("Лайк убран!")
    else:
        flash("Вы не ставили лайк на этот пост.")

    return redirect(url_for('posts.list_posts'))