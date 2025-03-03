from flask import Blueprint, render_template, redirect,url_for ,flash

from application.decorators import login_required, moderator_required 
from ..models import Post , ModerationLog ,db 

moderation_bp=Blueprint("moderation",__name__) 

@moderation_bp.route("/moderate",methods=["GET"])
@login_required
@moderator_required('moderator')
def moderate_posts(): 
    posts=Post.query.all() # Получаем все посты для модерации 
    return render_template("moderate_posts.html",posts=posts) 

@moderation_bp.route("/approve/<int:post_id>",methods=["POST"])
@login_required
def approve_post(post_id): 
    post=Post.query.get_or_404(post_id) 
    
    log_entry=ModerationLog(post_id=post.id, status="approved") 
    
    post.is_active=True # Устанавливаем статус поста как активный 
    
    # Добавляем запись в лог модерации 
    
    db.session.add(log_entry) 
    
    # Сохраняем изменения в базе данных 
    
    db.session.commit() 
    
    flash(f"Post {post.id} approved!") 
    
    return redirect(url_for("moderation.moderate_posts")) 

@moderation_bp.route("/reject/<int:post_id>",methods=["POST"])
@login_required
def reject_post(post_id): 
    post=Post.query.get_or_404(post_id) 
    
    log_entry=ModerationLog(post_id=post.id,status="rejected") 
    
    post.is_active=False # Устанавливаем статус поста как неактивный 
    
    # Добавляем запись в лог модерации 
    
    db.session.add(log_entry) 
    
    # Сохраняем изменения в базе данных 
    
    db.session.commit() 
    
    flash(f"Post {post.id} rejected!") 
    
    return redirect(url_for("moderation.moderate_posts")) 