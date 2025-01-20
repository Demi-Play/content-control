import os
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from application.decorators import login_required
from ..models import Like, db, Post, Comment
from ..forms import PostForm
from ..app import app, transliterate_filename
from werkzeug.utils import secure_filename


posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
def list_posts():
    posts = Post.query.options(joinedload(Post.author)).filter_by(is_active=True).all()
    return render_template('posts.html', posts=posts)

@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    
    
    if form.validate_on_submit():
        
        content_text = form.content_text.data
        
        # Обработка загрузки файла
        file_path = None
        new_filename = None  # Инициализация переменной
        
        if form.file.data:
            file_path = secure_filename(form.file.data.filename)  # Безопасное имя файла
            
            new_filename = transliterate_filename(file_path)
            # Сохраняем файл в папку uploads (необходимо создать эту папку заранее!)
            form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        
        new_post = Post(user_id=session['user_id'], content_text=content_text,
                        file_path=new_filename,
                        file_type='image' if file_path and file_path.endswith(('png', 'jpg', 'jpeg')) else 'video')
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('Публикация успешно создана!')
        return redirect(url_for('posts.list_posts'))
    
    return render_template('new_post.html', form=form)

@posts_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != session.get('user_id'):
        flash('У вас нет необходимых разрешений для изменения данной публикации.')
        return redirect(url_for('posts.list_posts'))

    form = PostForm(obj=post)  # Заполняем форму данными поста
    
    if form.validate_on_submit():
        post.content_text = form.content_text.data
        
        # Обработка загрузки нового файла (если есть)
        if form.file.data:
            file_path_new_file_name= secure_filename(form.file.data.filename)
            new_filename = transliterate_filename(file_path_new_file_name)
            
            form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            post.file_path=new_filename
             
            if new_filename and new_filename.endswith(('png', 'jpg', 'jpeg')):
                post.file_type='image'
            else: 
                post.file_type = 'video'
        
        db.session.commit()
        
        flash('Публикация успешно обновлена!')
        return redirect(url_for('posts.list_posts'))
    
    return render_template('edit_post.html', form=form)

@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != session.get('user_id'):
        flash('У вас нет необходимых разрешений для удаления данной публикации.')
        return redirect(url_for('posts.list_posts'))
    else:
        comments = Comment.query.filter_by(post_id=post.id).all()
        for comment in comments:
            db.session.delete(comment)

        # Удаляем лайки к посту
        likes = Like.query.filter_by(post_id=post.id).all()
        for like in likes:
            db.session.delete(like)
        db.session.delete(post)
        

    post.is_active = False  # Логическое удаление поста
    
    db.session.commit()
    
    flash('Публикация успешно удалена!')
    return redirect(url_for('posts.list_posts'))