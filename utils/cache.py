import functools
import json
import time
from redis import StrictRedis, WatchError
redis = StrictRedis()
pipe = redis.pipeline()


def auto_commit(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        try:
            isbn = args[0]
            print(isbn)
            pipe.watch(isbn)
            pipe.multi()
            f(*args, **kwargs)
            pipe.execute()
        except WatchError:
            print("WatchError")
            pass
    return decorator


class BookCache:

    @staticmethod
    def get_from_redis(isbn):
        timestamp = redis.zscore('book_isbn', isbn)
        if timestamp:
            json_book = redis.zrangebyscore('book_data', timestamp, timestamp)  # 返回的是列表
            if json_book:
                book = json.loads(json_book[0])
                BookCache.update(isbn, book)
                return book
        return None

    @staticmethod
    def recent():
        json_books = redis.zrevrange('book_data', 0, -1)
        books = [json.loads(book) for book in json_books]
        return books

    @staticmethod
    @auto_commit
    def update(isbn, book):
        print('update')
        timestamp = time.time()
        json_book = json.dumps(book)

        book_count = redis.zcard('book_isbn')

        pipe.zadd('book_isbn', {isbn: timestamp})
        pipe.zadd('book_data', {json_book: timestamp})
        if book_count >= 30:
            pipe.zremrangebyscore('book_isbn', 0, 0)   # 从小到大排序，删除第一个即为从大到小排序删除最后一个
            pipe.zremrangebyscore('book_data', 0, 0)


if __name__ == '__main__':

    book = {'author': '金庸', 'isbn': 1234567890, 'title': '天龙八部'}
    isbn = 1234567890

    books = BookCache.recent()
    print(books)
    json_book = redis.zrangebyscore('book_data', 0, 0)

    # BookCache.update(isbn, book)
    # time.sleep(1)
    # book = BookCache.get_from_redis(isbn)

# timestamp = time.time()
# redis.zadd('book_isbn', {isbn: timestamp})
