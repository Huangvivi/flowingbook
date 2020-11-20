from flask import Blueprint, jsonify, request, render_template, flash
from flask_login import current_user

from flowingbook.utils.helper import is_isbn_or_key
from .blueprint import views
from ..forms.bookform import SearchForm
from flowingbook.view_models.book import BookViewModel, BookCollection
from flowingbook.utils.spider import FlowingBook
from ..models.gift import Gift
from ..models.wish import Wish
from ..view_models.trade import TradeInfo


@views.route("/book/search")
def search():
    form = SearchForm(request.args)
    books = BookCollection()

    if form.validate():
        q = form.q.data.strip()
        page = form.page.data
        isbn_or_key = is_isbn_or_key(q)
        flowingbook = FlowingBook()

        if isbn_or_key == 'isbn':
            flowingbook.search_by_isbn(q)
        else:
            flowingbook.search_by_keyword(q, page)

        # books.fill(flowingbook.search_by_keyword(q, page), q)
        books.fill({'books': flowingbook.books, 'total': flowingbook.total}, q)
    else:
        flash('搜索的关键字不符合要求，请重新输入关键字')

    return render_template('search_result.html', books=books, form=form)


@views.route('/book/<isbn>/detail')
def book_detail(isbn):
    has_in_gifts = False
    has_in_wishes = False

    # 取书籍详情数据
    flowingbook = FlowingBook()
    flowingbook.search_by_isbn(isbn)
    book = BookViewModel(flowingbook.first)

    # MVC MVT

    if current_user.is_authenticated:
        if Gift.query.filter_by(uid=current_user.id, isbn=isbn,
                                launched=False).first():
            has_in_gifts = True
        if Wish.query.filter_by(uid=current_user.id, isbn=isbn,
                                launched=False).first():
            has_in_wishes = True

    trade_gifts = Gift.query.filter_by(isbn=isbn, launched=False).all()
    trade_wishes = Wish.query.filter_by(isbn=isbn, launched=False).all()

    trade_wishes_model = TradeInfo(trade_wishes)
    trade_gifts_model = TradeInfo(trade_gifts)

    return render_template('book_detail.html',
                           book=book, wishes=trade_wishes_model,
                           gifts=trade_gifts_model, has_in_wishes=has_in_wishes,
                           has_in_gifts=has_in_gifts)


@views.route("/base_test")
def base_test():
    book = {'author': '村上春树美食书友会', 'title': '村上春树美食厨房', 'publisher': '中国轻工业出版社', 'price': '20.00', 'image': 'https://img3.doubanio.com/lpic/s1170102.jpg', 'summary': '如同“胃是通向爱人之心的捷径”，这一次，请用绽放的味蕾，体味接触村上春树最感性的方式。\\n喜爱村上春树的书迷们，绝不会错过这一场以最私人化的感性方式，接触到心仪作家内心最本质部分的华丽盛宴！\\n这既是一本完全村上风格的随笔，又是一本不折不扣的标准食谱，糅合了村上春树令人着魔的文字魅力与极具作家私人偏好的美食诱惑，从希腊到意大利，从露天市场到晨曦中的渔港，请追随作家在声色香浓的欧洲，'}

    books = []
    books.append(book)
    for book in books:
        print(book['author'])
    return render_template("base_test.html", books=books)


@views.route("/test")
def test():
    return render_template("test2.html")