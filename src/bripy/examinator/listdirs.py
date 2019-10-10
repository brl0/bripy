from pathlib import Path
from pprint import pprint
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import (Process, JoinableQueue as Queue, freeze_support)
from time import sleep
import sys

from bripy.bllb.bllb_logging import get_dbg, setup_logging

EXECUTOR = ProcessPoolExecutor

logger = setup_logging(True, "DEBUG", loguru_enqueue=True)
DBG = get_dbg(logger)

basepath = '.'
NUMBER_OF_PROCESSES = 4


def worker(input, output):
    while not input.empty() or input.qsize():
        item = input.get()
        DBG(item)
        path = Path(item)
        dirs = map(str, filter(Path.is_dir, path.iterdir()))
        [*map(input.put, dirs)]
        output.put(item)
        input.task_done()


@logger.catch
def main():
    s = time.perf_counter()

    task_q = Queue()
    done_q = Queue()
    task_q.put(basepath)

    processes = [
        Process(target=worker, args=(task_q, done_q))
        for _ in range(NUMBER_OF_PROCESSES)
    ]

    for process in processes:
        process.start()

    # with EXECUTOR(max_workers=NUMBER_OF_PROCESSES) as executor:
    #     futures = []
    #     results = []
    #     while not task_q.empty() or task_q.qsize():
    #         futures.append(executor.submit(worker, task_q, done_q))
    #         results.append(futures[-1].result())
    #         DBG(task_q.qsize())
    #worker(task_q, done_q)

    while not task_q.empty() or task_q.qsize():
        DBG(task_q.qsize())

    logger.info(f'task_q qsize: {task_q.qsize()}')
    task_q.join()

    # for process in processes:
    #     process.terminate()

    print(f'done_q qsize: {done_q.qsize()}')
    sleep(0.05)
    i, j = 0, 0
    dir_set = set()
    dir_list = list()
    while not done_q.empty():
        item = done_q.get()
        DBG(item)
        dir_set.add(str(Path(item).resolve()))
        dir_list.append(str(Path(item).resolve()))
        i += len([*Path(item).iterdir()])
        j += 1
        done_q.task_done()
    print(f'done_q qsize: {done_q.qsize()}')

    print(f'dir_list: {len(dir_list)}')
    print(f'dir_set: {len(dir_set)}')
    print(f'done_q count: {j}')
    print(f'done_q sum count: {i}')

    all_items = [*Path(basepath).rglob('*')]
    dir_items = [*filter(Path.is_dir, all_items)]
    dir_items_set = set([str(Path(item).resolve()) for item in dir_items])

    print(f'dir items set: {len(dir_items_set)}')
    print(f'dir items: {len(dir_items)}')
    print(f'Total items: {len(all_items)}')

    diff = dir_items_set - dir_set
    print(f'diff: {diff}')
    diff2 = dir_set - dir_items_set
    print(f'diff2: {diff2}')

    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.".format())


if __name__ == '__main__':
    #freeze_support()
    sys.exit(main())
