from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from time import perf_counter, sleep
from multiprocessing import Manager
import sys

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData
from sqlalchemy.exc import IntegrityError
import pandas as pd
from tqdm import tqdm

from bripy.examinator.examinator import get_stat, md5_blocks

basepath = r'C:\Users\b_r_l\OneDrive\Documents\code'
output = r'fileinfo.csv'
database = r'big_glob.db'

EXECUTOR = ThreadPoolExecutor
MAX_WORKERS = 8


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
        if path.is_file():
            info['md5'] = md5_blocks(item)
        results.append(info)
        q.task_done()
    return False


if __name__ == '__main__':

    def main():
        engine = create_engine(f'sqlite:///{database}')
        if not Path(database).exists():
            metadata = MetaData()
            files = Table('files', metadata,
                          Column('path', String, index=True, primary_key=True))
            metadata.create_all(engine)
        else:
            metadata = MetaData(engine)
            files = Table('files',
                          metadata,
                          autoload=True,
                          autoload_with=engine)
        connection = engine.connect()

        with Manager() as manager:
            q = manager.JoinableQueue()
            results = manager.list()
            with EXECUTOR(max_workers=MAX_WORKERS) as executor:
                futures = []
                for _ in range(MAX_WORKERS):
                    future = executor.submit(worker, q, results)
                    futures.append(future)
                for path in tqdm(Path(basepath).rglob('*')):
                    try:
                        connection.execute(files.insert({'path': str(path)}))
                    except IntegrityError:
                        pass
                    else:
                        q.put(str(path))
                print("Done loading queue.")
                q.join()
                for _ in range(MAX_WORKERS):
                    q.put(None)
                q.join()
                success = all([future.result() for future in futures])
                if results:
                    df = pd.DataFrame.from_records(results)
                    df = df.set_index('path_hash')
                    print(df.info())
                    df.to_csv(output)
        print('FIN', success, perf_counter())
        return 0 if success else 1

    sys.exit(main())
