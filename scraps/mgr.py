from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Manager, Process
from pathlib import Path
from time import perf_counter, sleep

EXECUTOR = ThreadPoolExecutor
MAX_WORKERS = 4
basepath = r"C:\Users\b_r_l\OneDrive\Documents\code"


def worker(q, r):
    if not q.empty() or q.qsize():
        item = q.get()
        r.put(item)
        path = Path(item)
        dirs = filter(Path.is_dir, path.iterdir())
        [*map(q.put, dirs)]
        q.task_done()


def watch_out(r):
    i = 0
    while True:
        if not r.empty() or r.qsize():
            item = r.get()
            if item == "STOP":
                print(f"STOP {perf_counter()}")
                return
            print(i, perf_counter(), item)
            i += 1
            r.task_done()
        else:
            print(r.empty(), r.qsize())
            sleep(0.01)


if __name__ == "__main__":
    with Manager() as manager:
        q = manager.Queue()
        r = manager.Queue()
        q.put(basepath)
        r.put("START")
        p = Process(target=watch_out, args=(r,))
        p.start()
        with EXECUTOR(max_workers=MAX_WORKERS) as executor:
            futures, results = [], []
            while not q.empty() or q.qsize() or len(futures):
                if not q.empty() or q.qsize():
                    future = executor.submit(
                        worker,
                        q,
                        r,
                    )
                    futures.append(future)
                elif len(futures):
                    if any([map(lambda f: f.done(), futures)]):
                        for future in futures:
                            if future.done():
                                result = future.result()
                                results.append(result)
                                futures.remove(future)
                    else:
                        if len(futures) == 1:
                            future = futures[0]
                            result = future.result()
                            results.append(result)
                            futures.remove(future)
                        assert not any([map(lambda f: f.exception(), futures)])
                        assert not any([map(lambda f: f.cancelled(), futures)])
            while p.is_alive():
                print("STOPPING")
                r.put("STOP")
            q.join()
            p.join()
        print(f"FIN {perf_counter()}")
