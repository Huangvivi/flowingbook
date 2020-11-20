from celery import Celery

broker = 'redis://127.0.0.1:6379'
backend = 'redis://127.0.0.1:6379'


celery = Celery('my_tasks', broker=broker, backend=backend)


@celery.task
def add(x, y):
    print('add result: ', x + y)
    return x + y