from flask import Blueprint, session, redirect, url_for, flash
from ..models import db, Like

likes_bp = Blueprint('likes', __name__)

@likes_bp.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        flash("You need to be logged in to like a post.")
        return redirect(url_for('auth.login'))

    existing_like = Like.query.filter_by(post_id=post_id, user_id=session['user_id']).first()

    if existing_like:
        flash("You've already liked this post.")
    else:
        new_like = Like(post_id=post_id, user_id=session['user_id'])
        db.session.add(new_like)
        db.session.commit()
        flash("Post liked!")

    return redirect(url_for('posts.list_posts'))

@likes_bp.route('/unlike/<int:post_id>', methods=['POST'])
def unlike_post(post_id):
    if 'user_id' not in session:
        flash("You need to be logged in to unlike a post.")
        return redirect(url_for('auth.login'))

    existing_like = Like.query.filter_by(post_id=post_id, user_id=session['user_id']).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        flash("Like removed!")
    else:
        flash("You haven't liked this post yet.")

    return redirect(url_for('posts.list_posts'))
