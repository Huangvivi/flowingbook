from flask import flash, url_for, redirect, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import or_, desc
from flowingbook.forms.bookform import TradeForm
from flowingbook.models.base import db
from flowingbook.models.gift import Gift
from flowingbook.models.trade import Trade
from flowingbook.models.user import User
from flowingbook.models.wish import Wish
from flowingbook.utils.email import send_mail
from flowingbook.utils.enums import PendingStatus
from flowingbook.view_models.book import BookViewModel
from flowingbook.view_models.trade import TradeCollection
from flowingbook.views.blueprint import views


@views.route('/trade/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_trade(gid):
    current_gift = Gift.query.get(gid)

    if current_gift.is_yourself_gift(current_user.id):
        flash('当前书籍是你自己的哟，不能向自己索要书籍')
        return redirect(url_for('views.book_detail', isbn=current_gift.isbn))

    can = current_user.can_send_drift()
    if not can:
        return render_template('not_enough_beans.html', beans=current_user.beans)

    form = TradeForm(request.form)
    if request.method == 'POST' and form.validate():
        save_trade(form, current_gift)
        send_mail(current_gift.user.email, '有人想要一本书', 'email/get_gift.html', wisher=current_user, gift=current_gift)
        return redirect(url_for("views.pending"))

    gifter = current_gift.user.summary
    return render_template('trade.html', gifter=gifter, user_beans=current_user.beans, form=form)


@views.route("/pending")
@login_required
def pending():
    trade = Trade.query.filter(or_(Trade.requester_id == current_user.id,
                                   Trade.gifter_id == current_user.id),
                               Trade.status == 1).order_by(
                               desc(Trade.create_time)).all()
    view_models = TradeCollection(trade, current_user.id).data
    return render_template('pending.html', trades=view_models)


@views.route('/trade/<int:tid>/redraw')
@login_required
def redraw_trade(tid):
    with db.auto_commit():
        trade = Trade.query.filter_by(id=tid).first_or_404()
        trade.pending = PendingStatus.Redraw
    return redirect(url_for('views.pending'))


@views.route('/trade/<int:tid>/mailed')
@login_required
def mailed_trade(tid):
    with db.auto_commit():
        drift = Trade.query.filter_by(
            gifter_id=current_user.id, id=tid).first_or_404()
        drift.pending = PendingStatus.Success
        current_user.beans += 1
        gift = Gift.query.filter_by(id=drift.gift_id).first_or_404()
        gift.launched = True

        #  A  Wish
        #  A  Drift
        wish = Wish.query.filter_by(isbn=drift.isbn, uid=drift.requester_id, launched=False).first_or_404()
        wish.launched = True
        return redirect(url_for('views.pending'))


@views.route('/trade/<int:tid>/reject')
@login_required
def reject_trade(tid):
    with db.auto_commit():
        drift = Trade.query.filter(Gift.uid == current_user.id,     # 这里用作超权防范
                                   Trade.id == tid).first_or_404()
        drift.pending = PendingStatus.Reject
        requester = User.query.get_or_404(drift.requester_id)
        requester.beans += 1
    return redirect(url_for('views.pending'))


def save_trade(trade_form, current_gift):
    with db.auto_commit():
        trade = Trade()
        trade_form.populate_obj(trade)

        trade.gift_id = current_gift.id
        trade.requester_id = current_user.id
        trade.requester_nickname = current_user.nickname
        trade.gifter_nickname = current_gift.user.nickname
        trade.gifter_id = current_gift.user.id

        book = BookViewModel(current_gift.book)

        trade.book_title = book.title
        trade.book_author = book.author
        trade.book_img = book.image
        trade.isbn = book.isbn

        current_user.beans -= 1

        db.session.add(trade)
