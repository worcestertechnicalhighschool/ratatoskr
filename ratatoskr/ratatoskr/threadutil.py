
from threading import Thread

# Makes the function being decorated function
# spawn a thread and execute asynchronously
# upon being called instead of executing synchronously
def daemon(func):
    def inner(*args, **kwargs):
        l = lambda: func(*args, **kwargs)
        Thread(daemon=True, target=l).start()
    return inner