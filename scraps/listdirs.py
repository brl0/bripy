import sys
import time
from multiprocessing import JoinableQueue as Queue
from multiprocessing import Process, freeze_support
from pathlib import Path
from pprint import pprint
from time import sleep

from bripy.bllb.logging import get_dbg, setup_logging

logger = setup_logging(True, "INFO", loguru_enqueue=True)
DBG = get_dbg(logger)

basepath = "."
NUMBER_OF_PROCESSES = 1


def worker(input_q, output_q):
    while True or not input_q.empty() or input_q.qsize():
        item = input_q.get()
        if not item:
            sleep(0.05)
            DBG("no item")
            continue
        if item == "STOP":
            logger.info("Stopping...")
            input_q.task_done()
            return
        DBG(item)
        path = Path(item)
        dirs = map(str, filter(Path.is_dir, path.iterdir()))
        [*map(input_q.put, dirs)]
        output_q.put(item)
        input_q.task_done()


def get_q(q):
    results = []
    while not q.empty() or q.qsize():
        item = q.get()
        if item == "STOP":
            DBG("STOP get_q")
            q.task_done()
            break
        DBG(item)
        if item:
            results.append(item)
        q.task_done()
    return results


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

    while not task_q.empty() or task_q.qsize():
        DBG(task_q.qsize())
        sleep(0.05)

    logger.info(f"task_q qsize: {task_q.qsize()}")
    task_q.join()

    for _ in range(NUMBER_OF_PROCESSES):
        task_q.put("STOP")

    while (
        not task_q.empty()
        or task_q.qsize()
        or any(map(lambda p: p.is_alive(), processes))
    ):
        DBG(task_q.qsize())
        sleep(0.05)

    for process in processes:
        process.terminate()

    for process in processes:
        process.close()

    for process in processes:
        try:
            process.join()
        except ValueError:
            ...

    print(f"done_q qsize: {done_q.qsize()}")
    sleep(0.05)

    future = Process(target=get_q, args=(done_q,))
    done_q.put("STOP")
    done_q.join()
    dir_list = future.result()

    dir_set = set(dir_list)
    print(f"done_q qsize: {done_q.qsize()}")

    print(f"dir_list: {len(dir_list)}")
    print(f"dir_set: {len(dir_set)}")
    print(f"done_q count: {j}")
    print(f"done_q sum count: {i}")

    all_items = [*Path(basepath).rglob("*")]
    dir_items = [*filter(Path.is_dir, all_items)]
    dir_items_set = {str(Path(item).resolve()) for item in dir_items}

    print(f"dir items set: {len(dir_items_set)}")
    print(f"dir items: {len(dir_items)}")
    print(f"Total items: {len(all_items)}")

    diff = dir_items_set - dir_set
    print(f"diff: {diff}")
    diff2 = dir_set - dir_items_set
    print(f"diff2: {diff2}")

    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.".format())


if __name__ == "__main__":
    freeze_support()
    sys.exit(main())
