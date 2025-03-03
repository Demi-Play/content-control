from flask import Blueprint, session, redirect, url_for, flash, request, render_template
from flask_login import current_user, login_required
from application.content_analysis import ContentModerator
from ..models import ModerationLog, db, Comment, Post
from ..forms import CommentForm

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/post/<int:post_id>/comments', methods=['GET'])
def list_comments(post_id):
    form = CommentForm()
    post=Post.query.get_or_404(post_id) 
    comments=Comment.query.filter_by(post_id=post.id).all() 
    return render_template("comments.html", post=post , comments=comments, form=form) 

@comments_bp.route('/post/<int:post_id>/comment/new', methods=['POST'])
@login_required
def add_comment(post_id):
    # flash("Вы должны быть авторизованы для того, чтобы оставлять комментарии.")
    # return redirect(url_for("auth.login"))

    text = request.form.get("text")
    
    # Инициализация модератора контента
    moderator = ContentModerator()
    
    # Проверка комментария
    if moderator.moderate_comment(text):
        # Если комментарий не прошел модерацию
        flash("Комментарий содержит неприемлемый контент и был заблокирован.")
        return redirect(url_for('posts.list_posts'))
    
    # Если комментарий прошел модерацию
    new_comment = Comment(
        post_id=post_id, 
        user_id=session['user_id'], 
        text=text
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    flash("Комментарий добавлен!")
    return redirect(url_for("comments.list_comments", post_id=post_id))

@comments_bp.route('/post/<int:post_id>/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Проверка прав доступа к редактированию комментария
    if comment.user_id != session.get('user_id'):
        flash('У вас нет прав для редактирования этого комментария.')
        return redirect(url_for("comments.list_comments", post_id=post_id))

    if request.method == 'POST':
        new_text = request.form.get("text")
        
        # Инициализация модератора контента
        moderator = ContentModerator()
        
        # Проверка нового текста комментария
        if moderator.moderate_comment(new_text):
            # Если комментарий не прошел модерацию
            flash("Комментарий содержит неприемлемый контент и был заблокирован.")
            return redirect(url_for('posts.list_posts'))
            
        # Если комментарий прошел модерацию
        comment.text = new_text
        db.session.commit()
        
        flash("Комментарий обновлён!")
        return redirect(url_for("comments.list_comments", post_id=post_id))

    return render_template("edit_comment.html", post=Post.query.get_or_404(post_id), comment=comment)

@comments_bp.route('/post/<int:post_id>/comment/<int:comment_id>/delete' , methods=['POST']) 
def delete_comment(post_id , comment_id): 
    comment=Comment.query.get_or_404(comment_id) 

    db.session.delete(comment) 
    db.session.commit() 

    flash("Comment deleted!") 
    return redirect(url_for("comments.list_comments" , post_id=post_id)) 