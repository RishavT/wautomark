from threading import Lock
from time import sleep
from datetime import datetime
import concurrent.futures
import functools
from uuid import uuid4
import random

LOCK = Lock()
TEMP = 0

def singleargs(func):

    @functools.wraps(func)
    def wrapped(args):
        return func(*args)

    return wrapped

asd = uuid4().hex

@singleargs
def f(x=None, y=None):
    print(x,y)
    sleep(int(random.random() * 4))
    lol(f"{x}*{y}={x*y}")
    return x*y

def lol(x):
    global TEMP
    LOCK.acquire()
    a = TEMP
    sleep(1)
    TEMP = a + 1
    print(asd, x, TEMP)
    LOCK.release()
    # asd = open("helloworld").read()
    # asd += x
    # with open("helloworld", "a") as f:
    #     f.write(asd)

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        start = datetime.now()
        argmap = [(x, x+1) for x in range(30)]
        # print(p.starmap(f, starmap=argmap))
        # future_to_url = { executor.submit(f, *args) for args in argmap }
        print([x for x in executor.map(f, argmap)])
        end = datetime.now()
        print(start, end, end-start)

