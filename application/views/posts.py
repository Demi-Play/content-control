import os
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.utils import secure_filename
from ..models import db, Post
from ..forms import PostForm
from ..app import app

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
def list_posts():
    posts = Post.query.filter_by(is_active=True).all()
    return render_template('posts.html', posts=posts)

@posts_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    
    if form.validate_on_submit():
        content_text = form.content_text.data
        
        # Обработка загрузки файла
        file_path = None
        if form.file.data:
            file_path = secure_filename(form.file.data.filename)  # Безопасное имя файла
            
            # Сохраняем файл в папку uploads (необходимо создать эту папку заранее!)
            form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], file_path))
        
        new_post = Post(user_id=session['user_id'], content_text=content_text,
                        file_path=file_path,
                        file_type='image' if file_path and file_path.endswith(('png', 'jpg')) else 'video')
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('Post created successfully!')
        return redirect(url_for('posts.list_posts'))
    
    return render_template('new_post.html', form=form)

@posts_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != session.get('user_id'):
        flash('You do not have permission to edit this post.')
        return redirect(url_for('posts.list_posts'))

    form = PostForm(obj=post)  # Заполняем форму данными поста
    
    if form.validate_on_submit():
        post.content_text = form.content_text.data
        
        # Обработка загрузки нового файла (если есть)
        if form.file.data:
            file_path_new_file_name= secure_filename(form.file.data.filename)  
            form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], file_path_new_file_name))
            post.file_path=file_path_new_file_name
        
        db.session.commit()
        
        flash('Post updated successfully!')
        return redirect(url_for('posts.list_posts'))
    
    return render_template('edit_post.html', form=form)

@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != session.get('user_id'):
        flash('You do not have permission to delete this post.')
        return redirect(url_for('posts.list_posts'))

    post.is_active = False  # Логическое удаление поста
    
    db.session.commit()
    
    flash('Post deleted successfully!')
    return redirect(url_for('posts.list_posts'))