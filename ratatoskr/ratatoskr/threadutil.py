from concurrent.futures import ThreadPoolExecutor
from threading import Thread

# Makes the function being decorated function
# spawn a thread and execute asynchronously
# upon being called instead of executing synchronously.
# uhh dont use this, use threadpool_decorator
def daemon(func):
    def inner(*args, **kwargs):
        l = lambda: func(*args, **kwargs)
        Thread(daemon=True, target=l).start()
    return inner

# Returns a decorator that can be attached to any function to have
# it execute asynchronously on a limited number of threads.
def threadpool_decorator(threads=None):
    pool = ThreadPoolExecutor(threads)
    def decorator(func):
        def inner(*args, **kwargs):
            pool.submit(func, *args, **kwargs)
        return inner
    return decorator
