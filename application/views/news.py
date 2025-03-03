from flask import Blueprint, render_template, redirect, url_for, flash
from ..models import News, db
from ..forms import NewsForm
from application.decorators import login_required

news_bp = Blueprint('news', __name__)

@news_bp.route('/news')
@login_required
def list_news():
    news_items = News.query.all()
    return render_template('news.html', news_items=news_items)

@news_bp.route('/news/new', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        news = News(title=form.title.data, content=form.content.data)
        db.session.add(news)
        db.session.commit()
        flash('News added successfully!')
        return redirect(url_for('news.list_news'))
    return render_template('add_news.html', form=form)

@news_bp.route('/news/edit/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    news_item = News.query.get_or_404(news_id)
    form = NewsForm(obj=news_item)
    if form.validate_on_submit():
        news_item.title = form.title.data
        news_item.content = form.content.data
        db.session.commit()
        flash('News updated successfully!')
        return redirect(url_for('news.list_news'))
    return render_template('edit_news.html', form=form, news_item=news_item)

@news_bp.route('/news/delete/<int:news_id>', methods=['POST'])
@login_required
def delete_news(news_id):
    news_item = News.query.get_or_404(news_id)
    db.session.delete(news_item)
    db.session.commit()
    flash('News deleted successfully!')
    return redirect(url_for('news.list_news')) 