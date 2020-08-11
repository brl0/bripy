from queue import Queue
from threading import Thread
from time import sleep

from bripy.bllb.logging import logger, DBG

def unloadq(q, stop, limit=2000, rest=.1, check=100):
    i = limit
    loops = 0
    results = []
    while True and ((i and not stop()) or q.qsize()):
        loops += 1
        if loops % check == 0:
            DBG(i, loops, len(results))
        if q.qsize():
            x = q.get()
            DBG(x)
            results.append(x)
            i = min(i + 1, limit)
        else:
            i -= 1
            if i % check == 0:
                DBG(i)
            sleep(rest)
    return results


def multiplex(n, q, **kwargs):
    """ Convert one queue into several equivalent Queues

    >>> q1, q2, q3 = multiplex(3, in_q)
    """
    out_queues = [Queue(**kwargs) for i in range(n)]

    def f():
        while True:
            x = q.get()
            for out_q in out_queues:
                out_q.put(x)

    t = Thread(target=f)
    t.daemon = True
    t.start()
    return out_queues


def push(in_q, out_q):
    while True:
        x = in_q.get()
        out_q.put(x)


def merge(*in_qs, **kwargs):
    """ Merge multiple queues together

    >>> out_q = merge(q1, q2, q3)
    """
    out_q = Queue(**kwargs)
    threads = [Thread(target=push, args=(q, out_q)) for q in in_qs]
    for t in threads:
        t.daemon = True
        t.start()
    return out_q


def iterq(q):
    while q.qsize():
        yield q.get()


def get_q(q):
    results = []
    while not q.empty() or q.qsize():
        item = q.get()
        if item == 'STOP':
            DBG('STOP get_q')
            q.task_done()
            break
        DBG(item)
        if item:
            results.append(item)
        q.task_done()
    return results
