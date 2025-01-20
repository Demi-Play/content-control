from flask import Blueprint, session, redirect, url_for, flash, request, render_template
from ..models import db, Comment, Post
from ..forms import CommentForm

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/post/<int:post_id>/comments', methods=['GET'])
def list_comments(post_id):
    post=Post.query.get_or_404(post_id) 
    comments=Comment.query.filter_by(post_id=post.id).all() 
    return render_template("comments.html", post=post , comments=comments) 

@comments_bp.route('/post/<int:post_id>/comment/new', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash("Вы должны быть авторизованы для того, чтобы оставлять комментарии.")
        return redirect(url_for("auth.login"))

    text = request.form.get("text")
    
    new_comment = Comment(post_id=post_id, user_id=session['user_id'], text=text)
    
    db.session.add(new_comment)
    db.session.commit()
    
    flash("Комментарий добавлен!")
    
    return redirect(url_for("comments.list_comments", post_id=post_id))

@comments_bp.route('/post/<int:post_id>/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if request.method == 'POST':
        comment.text = request.form.get("text")
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