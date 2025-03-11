import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from application.content_analysis import ContentModerator
from ..models import Like, db, Post, Comment
from ..forms import PostForm
from ..app import app, transliterate_filename
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
def list_posts():
    posts = Post.query.options(joinedload(Post.author)).filter_by(is_active=True).all()
    return render_template('posts.html', posts=posts)

@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    
    # Инициализация модератора контента
    moderator = ContentModerator()
    
    if form.validate_on_submit():
        content_text = form.content_text.data
        
        # Проверка текста поста
        if moderator.moderate_comment(content_text):
            # Если пост не прошел модерацию
            flash('Публикация содержит неприемлемый контент.')
            return redirect(url_for('posts.list_posts'))
        
        # Обработка загрузки файла
        file_path = None
        new_filename = None  # Инициализация переменной
        
        if form.file.data:
            file_path = secure_filename(form.file.data.filename)  # Безопасное имя файла
            
            new_filename = transliterate_filename(file_path)
            # Сохраняем файл в папку uploads
            form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        
        new_post = Post(
            user_id=current_user.id, 
            content_text=content_text,
            file_path=new_filename,
            file_type='image',
            is_active=True  # По умолчанию пост активен
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('Публикация успешно создана!')
        return redirect(url_for('posts.list_posts'))
    
    return render_template('new_post.html', form=form)

@posts_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        flash('У вас нет необходимых разрешений для изменения данной публикации.')
        return redirect(url_for('posts.list_posts'))

    form = PostForm(obj=post)  # Заполняем форму данными поста
    
    # Инициализация модератора контента
    moderator = ContentModerator()
    
    if form.validate_on_submit():
        # Проверка текста поста
        if moderator.moderate_comment(form.content_text.data):
            # Если пост не прошел модерацию
            post.is_active = False
            db.session.commit()
            
            flash('Публикация содержит неприемлемый контент и была деактивирована.')
            return redirect(url_for('posts.list_posts'))
        
        post.content_text = form.content_text.data
        
        # Обработка загрузки нового файла (если есть)
        if form.file.data:
            file_path_new_file_name = secure_filename(form.file.data.filename)
            new_filename = transliterate_filename(file_path_new_file_name)
            
            form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            post.file_path = new_filename
            
            post.file_type = 'image'
        
        db.session.commit()
        
        flash('Публикация успешно обновлена!')
        return redirect(url_for('posts.list_posts'))
    
    return render_template('edit_post.html', form=form)

@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
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