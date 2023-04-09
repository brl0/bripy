import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Manager
from pathlib import Path
from time import perf_counter, sleep

import pandas as pd

from bripy.examinator.examinator import get_stat, md5_blocks

basepath = r"C:\Users\b_r_l\OneDrive\Documents\code"
output = "fileinfo.csv"

EXECUTOR = ThreadPoolExecutor
MAX_WORKERS = 40


def worker(q, results):
    while q:
        if q.empty() and not q.qsize():
            sleep(0.01)
            continue
        item = q.get()
        if item is None:
            q.task_done()
            return True
        path = Path(item)
        info = get_stat(item)
        if path.is_dir():
            [*map(q.put, path.iterdir())]
        elif path.is_file():
            info["md5"] = md5_blocks(item)
        results.append(info)
        q.task_done()
    return False


if __name__ == "__main__":

    def main():
        with Manager() as manager:
            q = manager.JoinableQueue()
            results = manager.list()
            q.put(basepath)
            with EXECUTOR(max_workers=MAX_WORKERS) as executor:
                futures = []
                for _ in range(MAX_WORKERS):
                    future = executor.submit(worker, q, results)
                    futures.append(future)
                q.join()
                for _ in range(MAX_WORKERS):
                    q.put(None)
                q.join()
                success = all([future.result() for future in futures])
                df = pd.DataFrame.from_records(results).set_index("path_hash")
            print(df.info())
            df.to_csv(output)
        print("FIN", success, perf_counter())
        return 0 if success else 1

    sys.exit(main())
