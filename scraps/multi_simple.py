from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Manager
from pathlib import Path
from time import perf_counter, sleep

basepath = r"C:\Users\b_r_l\OneDrive\Documents\code"
EXECUTOR = ThreadPoolExecutor
MAX_WORKERS = 40


def worker(q, results):
    i = 0
    while q:
        if q.empty() and not q.qsize():
            sleep(0.01)
            continue
        item = q.get()
        if item is None:
            q.task_done()
            break
        i += 1
        path = Path(item)
        all_items = [*path.iterdir()]
        [*map(q.put, filter(Path.is_dir, all_items))]
        [*map(results.append, all_items)]
        q.task_done()
    return i


if __name__ == "__main__":
    total = 0
    with Manager() as manager:
        q = manager.JoinableQueue()
        q.put(basepath)
        with EXECUTOR(max_workers=MAX_WORKERS) as executor:
            futures = []
            results = manager.list()
            for _ in range(MAX_WORKERS):
                future = executor.submit(worker, q, results)
                futures.append(future)
            q.join()
            for _ in range(MAX_WORKERS):
                q.put(None)
            total = sum([future.result() for future in futures])
            print(len(results))
    print("FIN", total, perf_counter())
