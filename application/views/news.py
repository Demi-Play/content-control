from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import News, db, UserActivity
from ..forms import NewsForm

news_bp = Blueprint('news', __name__)

@news_bp.route('/news')
def list_news():
    news_items = News.query.order_by(News.created_at.desc()).all()
    return render_template('news/news.html', news_items=news_items)

@news_bp.route('/news/add', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        news = News(
            title=form.title.data,
            content=form.content.data
        )
        db.session.add(news)
        
        # Логируем создание новости
        activity = UserActivity(
            user_id=current_user.id,
            action_type='create',
            target_type='news',
            target_id=news.id,
            details=f'Created news: {news.title}'
        )
        db.session.add(activity)
        
        db.session.commit()
        flash('Новость успешно добавлена!', 'success')
        return redirect(url_for('news.list_news'))
    return render_template('news/add_news.html', form=form)

@news_bp.route('/news/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    news = News.query.get_or_404(news_id)
    form = NewsForm(obj=news)
    
    if form.validate_on_submit():
        old_title = news.title
        news.title = form.title.data
        news.content = form.content.data
        
        # Логируем редактирование новости
        activity = UserActivity(
            user_id=current_user.id,
            action_type='edit',
            target_type='news',
            target_id=news.id,
            details=f'Edited news: {old_title} -> {news.title}'
        )
        db.session.add(activity)
        
        db.session.commit()
        flash('Новость успешно обновлена!', 'success')
        return redirect(url_for('news.list_news'))
    
    return render_template('news/edit_news.html', form=form, news=news)

@news_bp.route('/news/<int:news_id>/delete', methods=['POST'])
@login_required
def delete_news(news_id):
    news = News.query.get_or_404(news_id)
    title = news.title
    
    # Логируем удаление новости
    activity = UserActivity(
        user_id=current_user.id,
        action_type='delete',
        target_type='news',
        target_id=news_id,
        details=f'Deleted news: {title}'
    )
    db.session.add(activity)
    
    db.session.delete(news)
    db.session.commit()
    flash('Новость успешно удалена!', 'success')
    return redirect(url_for('news.list_news')) 