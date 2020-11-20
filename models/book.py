from sqlalchemy import Column, Integer, String

from flowingbook.models.base import db, Base


class Book(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    author = Column(String(30), default='未名')
    isbn = Column(String(15), nullable=False, unique=True)
    price = Column(String(20))
    binding = Column(String(20))
    summary = Column(String(1000))
    image = Column(String(80))
    pages = Column(Integer)
    publisher = Column(String(50))
    pubdata = Column(String(20))