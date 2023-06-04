#!/usr/bin/env python3
"""Console script for daskerator."""

import datetime as dt
import inspect
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from hashlib import md5
from operator import methodcaller
from pathlib import Path
from pprint import pprint as pp
from queue import Queue
from threading import Thread
from time import sleep

import click
import pandas as pd
from distributed import Client, LocalCluster

from bripy.bllb.log import setup_logging
from bripy.bllb.str import hash_utf8

LOG_ON = False
LOG_LEVEL = "WARNING"


def start_log(enable=True, lvl="WARNING"):
    log = setup_logging(enable, lvl, loguru_enqueue=True)  # , std_lib=True)
    log.info("examinator logging started")
    return log


def md5_blocks(path, blocksize=1024 * 2048) -> str:
    path = Path(path)
    if not path.is_dir():
        try:
            hasher = md5()
            with path.open("rb") as file:
                block = file.read(blocksize)
                while len(block) > 0:
                    hasher.update(block)
                    block = file.read(blocksize)
            return hasher.hexdigest()
        except Exception as error:
            log.warning(f"Error trying to hash item: {str(path)}\nError:\n{error}")
            return
    else:
        log.debug(f"Item is a directory and will not be hashed.  {str(path)}")
        return


def get_stat(path, opt_md5=True, opt_pid=False) -> dict:
    log.debug(path)
    try:
        path = Path(path)
        info = dict(
            [
                _
                for _ in inspect.getmembers(path.lstat())
                if not _[0].startswith("_") and not inspect.isbuiltin(_[1])
            ]
        )
        info.update(
            {
                _[0]: str(_[1])
                for _ in inspect.getmembers(path)
                if "__" not in _[0] and "<" not in str(_[1])
            }
        )
        info.update(
            {
                str(_[0]): methodcaller(_[0])(path)
                for _ in inspect.getmembers(path)
                if _[0].startswith("is_") and _[0] != "is_mount"
            }
        )
        info["path"] = str(path)
        info["path_hash"] = hash_utf8(str(path))
        info["f_atime"] = dt.datetime.fromtimestamp(info["st_atime"])
        info["f_ctime"] = dt.datetime.fromtimestamp(info["st_ctime"])
        info["f_mtime"] = dt.datetime.fromtimestamp(info["st_mtime"])
        if opt_md5:
            if not path.is_dir():
                try:
                    md5_hash = md5_blocks(path)
                    info["md5"] = md5_hash
                except:
                    log.warning(f"Could not hash item: {str(path)}")
            else:
                log.debug(f"Item is a directory and will not be hashed.  {str(path)}")
        if opt_pid:
            log.debug(f"working using OS pid: {os.getpid()}, opt_pid: {opt_pid}")
        return info
    except Exception as error:
        log.warning(error)
        return {"path": str(path)}


def glob_paths(path):
    try:
        path = Path(path)
        if path.is_dir():
            return path.rglob("*")
        else:
            return path
    except Exception as error:
        log.warning(error)


def load_dir(from_q, to_q, stop):
    limit = 300
    i = limit
    while True and ((i and not stop()) or from_q.qsize()):
        if from_q.qsize():
            l = from_q.get()
            if isinstance(l, list):
                for item in l:
                    to_q.put(item)
            i = min(i + 1, limit)
        else:
            i -= 1
            sleep(0.1)


def unloadq(q, stop, limit=2000, rest=0.1, check=100):
    i = limit
    loops = 0
    results = []
    while True and ((i and not stop()) or q.qsize()):
        loops += 1
        if loops % check == 0:
            log.debug(i, loops, len(results))
        if q.qsize():
            x = q.get()
            log.debug(x)
            results.append(x)
            i = min(i + 1, limit)
        else:
            i -= 1
            if i % check == 0:
                log.debug(i)
            sleep(rest)
    return results


def multiplex(n, q, **kwargs):
    """Convert one queue into several equivalent Queues

    >>> q1, q2, q3 = multiplex(3, in_q)
    """
    out_queues = [Queue(**kwargs) for i in range(n)]

    def f():
        while True:
            x = q.get()
            for out_q in out_queues:
                out_q.put(x)

    t = Thread(target=f)
    t.daemon = True
    t.start()
    return out_queues


def push(in_q, out_q):
    while True:
        x = in_q.get()
        out_q.put(x)


def merge(*in_qs, **kwargs):
    """Merge multiple queues together

    >>> out_q = merge(q1, q2, q3)
    """
    out_q = Queue(**kwargs)
    threads = [Thread(target=push, args=(q, out_q)) for q in in_qs]
    for t in threads:
        t.daemon = True
        t.start()
    return out_q


def get_dir(d):
    path = Path(d)
    if path.is_dir():
        return [str(_) for _ in path.iterdir()]


def iterq(q):
    while q.qsize():
        yield q.get()


def proc_paths(basepaths, opt_md5=True):
    q = Queue()
    remote_q = client.scatter(q)
    q1, q2 = multiplex(2, remote_q)
    list_q = client.map(get_dir, q1)
    l_q = client.gather(list_q)
    pstat = partial(get_stat, opt_md5=opt_md5, opt_pid=True)
    q3 = client.map(pstat, q2)
    result_q = client.gather(q3)
    qs = [q, remote_q, q1, q2, list_q, l_q, q3, result_q]

    with ThreadPoolExecutor() as t:
        stop_threads = False
        stop = lambda: stop_threads
        t.submit(load_dir, l_q, q, stop)
        [q.put(str(Path(path).resolve())) for path in basepaths]
        results_future = t.submit(unloadq, result_q, stop, limit=300)
        ilimit = 10
        i = ilimit
        while i:
            alive = sum([_q.qsize() for _q in qs])
            if alive:
                i = min(i + 1, ilimit)
                log.debug(f"{alive}, {i}")
            else:
                i -= 1
                log.debug(f"i: {i}")
            sleep(0.1)
        stop_threads = True
        # results_list = unloadq(result_q, limit=300)
        results_list = results_future.result()
        results = pd.DataFrame(results_list)

    return results


@click.command()
@click.option(
    "-b",
    "--basepaths",
    default=".",
    help="Base path.",
    multiple=True,
    type=click.Path(exists=True),
)
@click.option("-f", "--file", help="File path or - for stdin", type=click.File("r"))
@click.option(
    "-o",
    "--output",
    default=".",
    help="Output path.",
    multiple=False,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option("--md5/--no-md5", default=True)
@click.option("-v", "--verbose", count=True)
@click.argument("args", nargs=-1)
def main(basepaths, output, file, md5, verbose, args):
    """Console script for examinator."""
    # click documentation at http://click.pocoo.org/
    s = time.perf_counter()
    log_on = LOG_ON
    log_level = LOG_LEVEL
    if verbose:
        log_on = True
        log_level = max(4 - verbose, 1) * 10
    global log
    log = start_log(log_on, log_level)
    log.info(f"verbose: {verbose}")
    log.warning(f"\nlogs enabled: {log_on}\nlog_level: {log_level}")
    log.debug(f"basepaths: {basepaths}")
    log.debug(f"output: {output}")
    log.debug(f"{str(type(file))}")
    log.debug(f"Optional md5 hash: {md5}")
    log.debug(f"{args}")
    time.sleep(0.05)  # Sleep to let logging initialize

    global cluster, client
    cluster = LocalCluster(processes=True)
    client = Client(cluster)

    if not basepaths:
        basepaths = []
    else:
        basepaths = list(basepaths)
    log.debug(f"{str(type(basepaths))}")
    if file:
        basepaths += file.read().split("\n")
    log.debug(f"\n{str(type(basepaths))}\n{basepaths}\n")

    log.debug(client)

    try:
        result = proc_paths(basepaths, opt_md5=md5)
        log.debug(f"{str(type(result))}, {str(len(result))}")
        fields = ["path", "st_size"]
        if md5:
            fields.append("md5")
        pp(result.loc[:, fields])
    except Exception:
        log.exception("FAIL")
        return error

    elapsed = time.perf_counter() - s
    log.info(f"{__file__} executed in {elapsed:0.2f} seconds.".format())
    log.debug("\n\nFIN\n\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
