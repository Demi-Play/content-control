from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from application.decorators import moderator_required
from ..models import Post, ModerationLog, db

moderation_bp = Blueprint("moderation", __name__)

@moderation_bp.route("/moderate", methods=["GET"])
@login_required
@moderator_required('moderator')
def moderate_posts():
    posts = Post.query.all()
    return render_template("moderate_posts.html", posts=posts)

@moderation_bp.route("/approve/<int:post_id>", methods=["POST"])
@login_required
@moderator_required('moderator')
def approve_post(post_id):
    post = Post.query.get_or_404(post_id)
    log_entry = ModerationLog(post_id=post.id, status="approved")
    post.is_active = True
    db.session.add(log_entry)
    db.session.commit()
    flash(f"Post {post.id} approved!", 'success')
    return redirect(url_for("moderation.moderate_posts"))

@moderation_bp.route("/reject/<int:post_id>", methods=["POST"])
@login_required
@moderator_required('moderator')
def reject_post(post_id):
    post = Post.query.get_or_404(post_id)
    log_entry = ModerationLog(post_id=post.id, status="rejected")
    post.is_active = False
    db.session.add(log_entry)
    db.session.commit()
    flash(f"Post {post.id} rejected!", 'error')
    return redirect(url_for("moderation.moderate_posts")) 