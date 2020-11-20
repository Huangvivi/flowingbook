from flask import render_template

from flowingbook.models.gift import Gift
from flowingbook.utils.cache import BookCache
from flowingbook.view_models.book import BookViewModel
from flowingbook.views.blueprint import views


@views.route("/")
def index():
    recent_books = BookCache.recent()
    books = [BookViewModel(book) for book in recent_books]
    return render_template('index.html', recent=books)