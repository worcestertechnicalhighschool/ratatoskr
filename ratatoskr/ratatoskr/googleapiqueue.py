
from threading import Thread
from time import sleep

__queue = []
__busy_wait_thread = None

def __spawn_daemon(lamb):
    def try_inner():
        try:
            lamb()
        except:
            pass
    Thread(target=try_inner, daemon=True).start()

def __busy_waiter():
    global __queue
    while True:
        sleep(0.1)
        if len(__queue) == 0:
            continue
        __spawn_daemon(lambda: __queue[0].execute())
        __queue = __queue[1:]
        

def add_request_to_queue(req):
    __queue.append(req)

if __busy_wait_thread is None:
    __busy_wait_thread = Thread(target=__busy_waiter, daemon=True)
    __busy_wait_thread.start()