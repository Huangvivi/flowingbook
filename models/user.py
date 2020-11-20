from math import floor

from flask import current_app
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, Float
from werkzeug.security import generate_password_hash, check_password_hash
# from flowingbook import login_manager
from flowingbook import login_manager
from flowingbook.models.base import db, Base
from flowingbook.utils.enums import PendingStatus
from flowingbook.models.gift import Gift
from flowingbook.models.trade import Trade
from flowingbook.models.wish import Wish
from flowingbook.utils.helper import is_isbn_or_key
from flowingbook.utils.spider import FlowingBook
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(UserMixin, Base):
    id = Column(Integer, primary_key=True)
    nickname = Column(String(24), nullable=False)
    phone_number = Column(String(18), unique=True)
    _password = Column('password', String(128), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    beans = Column(Float, default=0)
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer, default=0)

    @property
    def password(self):
        return self._password

    # 提供一个接口，当外部使用setattr的时候能给_password赋值
    @password.setter
    def password(self, raw):
        # 通过内部算法给用户密码加密，数据库中保存到的用户密码不应为明文
        self._password = generate_password_hash(raw)

    # 确认用户密码
    def check_password(self, raw):
        return check_password_hash(self._password, raw)

    # 提供login_user()使用的验证身份的属性
    def get_id(self):
        return self.id

    # 确认用户身份，
    def can_save_to_list(self, isbn):
        if is_isbn_or_key(isbn) != 'isbn':
            return False
        flowingbook = FlowingBook()
        flowingbook.search_by_isbn(isbn)
        if not flowingbook.first:
            return False

        gifting = Gift.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        wishing = Wish.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()

        # 用户不能既为赠送者和所求者
        if not gifting and not wishing:
            return True
        else:
            return False

    def generate_token(self, expire=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expire)
        token = s.dumps({'id': self.id}).decode('utf-8')
        return token

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
            return data
        except Exception as e:
            return None

    @staticmethod
    def reset_password(token, password):
        data = User.verify_token(token)
        try:
            uid = data.get('id')
            if not uid:
                return False
            with db.auto_commit():
                user = User.query.get(uid)
                user.password = password
            return True
        except Exception as e:
            return False

    @property
    def summary(self):
        return dict(
            nickname=self.nickname,
            beans=self.beans,
            email=self.email,
            send_receive=str(self.send_counter) + '/' + str(self.receive_counter)
        )

    # 检查用户发起交易请求条件
    # 积分>=1、每索取两本书，自己必须送出一本书
    def can_send_drift(self):
        if self.beans < 1:
            return False
        success_gifts_count = Gift.query.filter_by(uid=self.id, launched=True).count()
        success_receive_count = Trade.query.filter_by(requester_id=self.id, pending=PendingStatus.Success).count()
        return True if \
            floor(success_receive_count / 2) <= floor(success_gifts_count) \
            else False


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
