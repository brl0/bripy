from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from time import perf_counter, sleep
from multiprocessing import Manager
import sys

import pandas as pd

from bripy.examinator.examinator import get_stat, md5_blocks
from bripy.bllb.bllb_str import hash_utf8

basepath = r'C:\Users\b_r_l\OneDrive\Documents\code'
output = 'fileinfo.csv'

EXECUTOR = ThreadPoolExecutor
MAX_DIR_WORKERS = 40
MAX_HASH_WORKERS = 8


def dir_worker(q, out_q, results):
    while q:
        if q.empty() and not q.qsize():
            sleep(0.01)
            continue
        item = q.get()
        if item is None:
            q.task_done()
            return True
        path = Path(item)
        [*map(q.put, filter(Path.is_dir, path.iterdir()))]
        [*map(out_q.put, filter(Path.is_file, path.iterdir()))]
        all_info = map(get_stat, path.iterdir())
        [*map(results.append, all_info)]
        q.task_done()
    return False


def hash_worker(hash_q, hashes):
    while hash_q:
        if hash_q.empty() and not hash_q.qsize():
            sleep(0.01)
            continue
        item = hash_q.get()
        if item is None:
            hash_q.task_done()
            return True
        hashes.append((hash_utf8(str(item)), md5_blocks(item)))
        hash_q.task_done()
    return False


if __name__ == '__main__':

    def main():
        with Manager() as manager:
            q = manager.JoinableQueue()
            results = manager.list()
            hash_q = manager.JoinableQueue()
            hashes = manager.list()
            q.put(basepath)
            with ProcessPoolExecutor(
                    max_workers=MAX_HASH_WORKERS) as processor:
                hash_futures = []
                for _ in range(MAX_HASH_WORKERS):
                    future = processor.submit(hash_worker, hash_q, hashes)
                    hash_futures.append(future)
                with EXECUTOR(max_workers=MAX_DIR_WORKERS) as executor:
                    futures = []
                    for _ in range(MAX_DIR_WORKERS):
                        future = executor.submit(dir_worker, q, hash_q,
                                                 results)
                        futures.append(future)
                    q.join()
                    for _ in range(MAX_DIR_WORKERS):
                        q.put(None)
                    success = all([future.result() for future in futures])
                    df = pd.DataFrame.from_records(results).set_index(
                        'path_hash')
                    print(df.info())
                for _ in range(MAX_HASH_WORKERS):
                    hash_q.put(None)
                hash_q.join()
                hash_success = all(
                    [future.result() for future in hash_futures])
                print(hash_success)
                hash_df = pd.DataFrame.from_records(
                    hashes, columns=['path_hash', 'md5'])
                hash_df = hash_df.set_index('path_hash')
                df = df.join(hash_df)
                print(df.info())
                df.to_csv(output)
        print('FIN', success, perf_counter())
        return 0 if success else 1

    sys.exit(main())
