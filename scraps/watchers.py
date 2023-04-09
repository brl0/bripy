from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Manager, Process
from pathlib import Path
from time import perf_counter, sleep

EXECUTOR = ProcessPoolExecutor
MAX_WORKERS = 4
basepath = r"C:\Users\b_r_l\OneDrive\Documents\code"


def watch_q(q, out):
    while True:
        if not q.empty() or q.qsize():
            item = q.get()
            if item == "STOP":
                return
            out.put(item)
            all_items = Path(item).iterdir()
            dirs = filter(Path.is_dir, all_items)
            [*map(q.put, dirs)]
            q.task_done()
        else:
            sleep(0.01)


def watch_out(out):
    i = 0
    while True:
        if not out.empty() or out.qsize():
            item = out.get()
            print(i, perf_counter(), item)
            if item == "STOP":
                return
            i += 1
        else:
            sleep(0.01)


if __name__ == "__main__":
    with Manager() as manager:
        q = manager.Queue()
        out = manager.Queue()
        q.put(basepath)
        out.put("START")
        with EXECUTOR(max_workers=MAX_WORKERS + 1) as executor:
            out_watcher = executor.submit(watch_out, out)
            q_watchers = []
            for _ in range(MAX_WORKERS):
                watcher = executor.submit(watch_q, q, out)
                q_watchers.append(watcher)
            while not q.empty() or q.qsize() or not out.empty() or out.qsize():
                sleep(0.05)
            for _ in range(MAX_WORKERS):
                q.put("STOP")
            out.put("STOP")
            q_results = [watcher.result() for watcher in q_watchers]
            out_results = out_watcher.result()
        print("FIN")
