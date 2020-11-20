from flask import current_app
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, desc, func
from sqlalchemy.orm import relationship

from flowingbook.models.base import db, Base
from flowingbook.models.wish import Wish
from flowingbook.utils.spider import FlowingBook


class Gift(Base):
    id = Column(Integer, primary_key=True)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False)
    # book = relationship('Book')
    # bid = Column(Integer, ForeignKey('user.id'))
    launched = Column(Boolean, default=False)

    @classmethod
    def get_user_gifts(cls, uid):
        gifts = Gift.query.filter_by(uid=uid, launched=False).order_by(
            desc(Gift.create_time)).all()
        return gifts

    @classmethod
    def get_wish_counts(cls, isbn_list):
        # 根据用户的想要送的书籍的isbn列表，获取每个isbn对应书籍的索求者的数量
        count_list = db.session.query(func.count(Wish.id), Wish.isbn).filter(
            Wish.launched == False, Wish.isbn.in_(isbn_list), Wish.status == 1).group_by(
            Wish.isbn).all()
        count_list = [{'count': c[0], 'isbn': c[1]} for c in count_list]
        return count_list

    @classmethod
    def recent(cls):
        # recent_gift = Gift.query.filter_by(launched=False).group_by(
        #     Gift.isbn).order_by(desc(Gift.create_time)).limit(
        #     current_app.config['RECENT_BOOK_COUNT']).distinct().all()
        # return recent_gift
        recent_gift = Gift.query.filter_by(
            launched=False).group_by(
            Gift.isbn).order_by(
            desc(Gift.create_time)).limit(
            current_app.config['RECENT_BOOK_COUNT']).all()
        return recent_gift

    @property
    def book(self):
        flowingbook = FlowingBook()
        flowingbook.search_by_isbn(self.isbn)
        return flowingbook.first

    def is_yourself_gift(self, current_user_id):
        if current_user_id == self.uid:
            return True
        return False

