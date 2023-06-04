import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Manager
from pathlib import Path
from threading import Thread
from time import perf_counter, sleep

import pandas as pd
from sqlalchemy import Column, MetaData, String, Table, create_engine
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm

from bripy.bllb.file import md5_blocks
from bripy.bllb.fs import get_stat

basepath = r"C:/local/projects/pystuff"
output_db = r"fileinfo.db"
database = r"tracking.db"

EXECUTOR = ThreadPoolExecutor
MAX_WORKERS = 40
BATCH_RECORDS = 1000


def db_batcher(results, job_done):
    engine = create_engine(f"sqlite:///{output_db}")
    total = 0
    while True:
        if job_done.is_set() or len(results) >= BATCH_RECORDS:
            batch = len(results)
            df = pd.DataFrame.from_records(results[:batch])
            del results[:batch]
            df.to_sql("files", engine, if_exists="append")
            total += batch
        if job_done.is_set() and not results:
            return total
        sleep(0.01)


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
            info["md5"] = md5_blocks(item)
        results.append(info)
        q.task_done()
    return False


if __name__ == "__main__":

    def main():
        engine = create_engine(f"sqlite:///{database}")
        if not Path(database).exists():
            metadata = MetaData()
            files = Table(
                "files", metadata, Column("path", String, index=True, primary_key=True)
            )
            metadata.create_all(engine)
        else:
            metadata = MetaData(engine)
            files = Table("files", metadata, autoload=True, autoload_with=engine)
        connection = engine.connect()

        with Manager() as manager:
            q = manager.JoinableQueue()
            results = manager.list()
            job_done = manager.Event()
            with EXECUTOR(max_workers=MAX_WORKERS) as executor:
                db_thread = executor.submit(db_batcher, results, job_done)
                futures = []
                for _ in range(MAX_WORKERS - 1):
                    future = executor.submit(worker, q, results)
                    futures.append(future)
                for path in tqdm(Path(basepath).rglob("*")):
                    try:
                        connection.execute(files.insert({"path": str(path)}))
                    except IntegrityError:
                        pass
                    else:
                        q.put(str(path))
                print("Done loading queue.")
                q.join()
                print("Stopping workers.")
                for _ in range(MAX_WORKERS - 1):
                    q.put(None)
                q.join()
                print("Stopping database worker.")
                job_done.set()
                total = db_thread.result()
                print(f"Result count: {total}")
                success = all([future.result() for future in futures])
        print("FIN", success, perf_counter())
        return 0 if success else 1

    sys.exit(main())
