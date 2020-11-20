from flask import render_template, current_app, flash, redirect, url_for
from flask_login import login_required, current_user

from flowingbook.models.trade import Trade
from flowingbook.models.wish import Wish
from flowingbook.utils.enums import PendingStatus
from flowingbook.view_models.gift import MyGifts
from flowingbook.views.blueprint import views
from flowingbook.models.base import db
from flowingbook.models.gift import Gift


@views.route('/my/gifts')
@login_required
def my_gifts():
    uid = current_user.id
    gifts_of_user = Gift.get_user_gifts(uid)
    gifts_isbn_list = [gift.isbn for gift in gifts_of_user]
    wish_counts = Gift.get_wish_counts(gifts_isbn_list)
    view_model = MyGifts(wish_counts, gifts_of_user)
    return render_template('my_gifts.html', gifts=view_model.gifts)


@views.route('/gifts/book/<isbn>')
@login_required
def save_to_gifts(isbn):
    if current_user.can_save_to_list(isbn):
        with db.auto_commit():
            gift = Gift()
            gift.isbn = isbn
            gift.uid = current_user.id
            current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
            db.session.add(gift)
    else:
        flash('这本书已添加至你的赠送清单或已存在于你的心愿清单，请不要重复添加')
    return redirect(url_for('views.book_detail', isbn=isbn))


@views.route('/gifts/<gid>/redraw')
@login_required
def redraw_from_gifts(gid):
    gift = Gift.query.filter_by(id=gid, launched=False).first_or_404()
    trade = Trade.query.filter_by(gift_id=gift.id, pending=PendingStatus.Waiting).first()
    if trade:
        flash('这个礼物正处于交易状态，请前往Trade处理该交易')
    else:
        with db.auto_commit():
            current_user.beans -= current_app.config['BEANS_UPLOAD_ONE_BOOK']
            gift.delete()
    return redirect(url_for('views.my_gifts'))
