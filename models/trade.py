from sqlalchemy import Column, SmallInteger, Integer, String, Boolean, ForeignKey, desc, func

from flowingbook.models.base import Base
from flowingbook.utils.enums import PendingStatus


class Trade(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 书籍信息
    isbn = Column(String(13))
    book_title = Column(String(50))
    book_author = Column(String(50))
    book_img = Column(String(100))

    # 请求者信息
    requester_id = Column(Integer)
    requester_nickname = Column(String(30))

    # 赠送者信息
    gifter_id = Column(Integer)
    gifter_nickname = Column(String(30))
    gift_id = Column(Integer)

    # 邮寄详情
    recipient_name = Column(String(30), nullable=False)
    address = Column(String(100), nullable=False)
    message = Column(String(100))
    mobile = Column(String(20), nullable=False)

    _pending = Column('pending', SmallInteger, default=1)

    @property
    def pending(self):
        return PendingStatus(self._pending)

    @pending.setter
    def pending(self, status):
        self._pending = status.value
