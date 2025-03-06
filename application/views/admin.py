from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from application.decorators import moderator_required
from ..models import Like, Post, db, User, Comment
from ..forms import UserEditForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users', methods=['GET'])
@moderator_required('admin')
def list_users():
    users = User.query.all()  # Получаем всех пользователей
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@moderator_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)  # Заполняем форму данными пользователя

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data  # Предполагаем, что у вас есть поле для роли в форме
        db.session.commit()
        flash("Пользователь обновлён!")
        return redirect(url_for('admin.list_users'))

    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@moderator_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Удаляем все связанные посты
    posts = Post.query.filter_by(user_id=user.id).all()
    for post in posts:
        # Удаляем комментарии к посту
        comments = Comment.query.filter_by(post_id=post.id).all()
        for comment in comments:
            db.session.delete(comment)

        # Удаляем лайки к посту
        likes = Like.query.filter_by(post_id=post.id).all()
        for like in likes:
            db.session.delete(like)

        # Удаляем сам пост
        db.session.delete(post)

    # Удаляем самого пользователя
    db.session.delete(user)
    db.session.commit()

    flash("Пользователь и все связанные данные удалены!")
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/admin/users/<int:user_id>/block', methods=['POST'])
@moderator_required('admin')
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('Вы не можете заблокировать самого себя', 'error')
        return redirect(url_for('admin.list_users'))
    
    user.is_blocked = True
    db.session.commit()
    flash(f'Пользователь {user.username} успешно заблокирован', 'success')
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/admin/users/<int:user_id>/unblock', methods=['POST'])
@moderator_required('admin')
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('Вы не можете разблокировать самого себя', 'error')
        return redirect(url_for('admin.list_users'))
    
    user.is_blocked = False
    user.failed_login_attempts = 0
    user.last_failed_login = None
    db.session.commit()
    flash(f'Пользователь {user.username} успешно разблокирован', 'success')
    return redirect(url_for('admin.list_users'))