
from threading import Thread


def daemon(func):
    def inner(*args, **kwargs):
        l = lambda: func(*args, **kwargs)
        Thread(daemon=True, target=l).spawn()
    return inner