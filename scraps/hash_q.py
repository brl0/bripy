import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from hashlib import md5
from multiprocessing import JoinableQueue as Queue
from multiprocessing import freeze_support
from pathlib import Path
from time import perf_counter, sleep

import pandas as pd
from sqlalchemy import create_engine

MAX_WORKERS = 16
EXECUTOR = ThreadPoolExecutor
q = Queue()
basepath = r"C:\Users\b_r_l\OneDrive\Documents\code\python"
q.put(basepath)


def worker(item):
    path = Path(item)
    if path.is_dir():
        return [*map(str, path.iterdir())]
    elif path.is_file():
        hasher = md5()
        try:
            hasher.update(path.read_bytes())
            return str(path), hasher.hexdigest()
        except:
            return str(path), ""
    else:
        return str(path), ""


def main():
    engine = create_engine("sqlite:///hash.db")

    with EXECUTOR(max_workers=MAX_WORKERS) as executor:
        futures = []
        dirs = []
        hashes = []
        while not q.empty() or q.qsize() or len(futures):
            if q.qsize():
                item = q.get()
                if Path(item).is_dir():
                    dirs.append(item)
                item_future = executor.submit(worker, item)
                futures.append(item_future)
                q.task_done()
            elif (q.empty() or not q.qsize()) and len(futures):
                for future in futures:
                    if future.done():
                        result = future.result()
                        futures.remove(future)
                        if isinstance(result, tuple):
                            hashes.append(result)
                        elif isinstance(result, list):
                            [*map(q.put, result)]
        q.join()
        df = pd.DataFrame(hashes, columns=["path", "md5"])
        df.to_sql("files", con=engine)
        print(df.head())
        print(df.info())
        print(f"dirs count: {len(dirs)}")
        print(f"len_hashes: {len(hashes)}")
        all_items = [*Path(basepath).rglob("*")]
        print(f"all_items len: {len(all_items)}")
        all_dirs = [*map(str, filter(Path.is_dir, all_items))]
        print(f"all_dirs: {len(all_dirs)}")
        diff = set(all_dirs).symmetric_difference(dirs)
        print(f"diff: {diff}")
        return 0


if __name__ == "__main__":
    freeze_support()
    print(perf_counter())
    result = main()
    print(perf_counter())
    sys.exit(result)
