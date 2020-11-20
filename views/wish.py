from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user

from flowingbook import limiter
from flowingbook.models.base import db
from flowingbook.models.gift import Gift
from flowingbook.models.wish import Wish
from flowingbook.utils.email import send_mail
from flowingbook.view_models.wish import MyWishes
from flowingbook.views.blueprint import views


def limit_key_prefix():
    isbn = request.args['isbn']
    uid = current_user.id
    return f"satisfy_wish/{isbn}/{uid}"


@views.route('/wish/book/<isbn>')
@login_required
def save_to_wish(isbn):
    if current_user.can_save_to_list(isbn):
        with db.auto_commit():
            wish = Wish()
            wish.uid = current_user.id
            wish.isbn = isbn
            db.session.add(wish)
    else:
        flash('这本书已添加至你的赠送清单或已存在于你的心愿清单，请不要重复添加')
    return redirect(url_for('views.book_detail', isbn=isbn))


@views.route("/my/wish")
@login_required
def my_wish():
    uid = current_user.id
    wishes_of_user = Wish.get_user_wishes(uid)
    isbn_list = [wish.isbn for wish in wishes_of_user]
    wish_counts = Wish.get_gifts_counts(isbn_list)
    view_model = MyWishes(wish_counts, wishes_of_user)
    return render_template('my_wish.html', wishes=view_model.gifts)


@views.route('/satisfy/wish/<int:wid>')
# @limiter.limit(key_func=limit_key_prefix)
@login_required
def satisfy_wish(wid):
    wish = Wish.query.get_or_404(wid)
    gift = Gift.query.filter_by(uid=current_user.id, isbn=wish.isbn).first()
    if not gift:
        flash('你还没有上传此书，'
              '请点击“加入到赠送清单”添加此书。添加前，请确保自己可以赠送此书')
    else:
        send_mail(wish.user.email,
                  '有人想送你一本书', 'email/satisfy_wish.html', wish=wish,
                  gift=gift)
        flash('已向他/她发送了一封邮件，如果他/她愿意接受你的赠送，你将收到一个鱼漂')
    return redirect(url_for('views.book_detail', isbn=wish.isbn))


@views.route('/wish/book/<isbn>/redraw')
@login_required
def redraw_from_wish(isbn):
    wish = Wish.query.filter_by(isbn=isbn, launched=False).first_or_404()
    with db.auto_commit():
        wish.delete()
    return redirect(url_for('views.my_wish'))


@limiter.limited
# @views.route('wish/book/satisfy')
def satisfy_with_limited():
    isbn = request.args['isbn']
    flash('你已向他发送过赠送邀请，请不要频繁发送')
    return redirect(url_for('views.book_detail', isbn=isbn))
