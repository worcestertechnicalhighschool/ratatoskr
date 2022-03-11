
from threading import Thread
from time import sleep

__queue = []
__busy_wait_thread = None

def __spawn_daemon(lamb):
    Thread(target=lamb, daemon=True).start()

def __busy_waiter():
    while True:
        sleep(0.1)
        if len(__queue) == 0:
            continue
        __spawn_daemon(__queue[:1].execute)
        

def add_request_to_queue(req):
    __queue.append(req)

if __busy_wait_thread is None:
    Thread(target=__busy_waiter, daemon=True)