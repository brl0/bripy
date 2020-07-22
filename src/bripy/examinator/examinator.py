"""Examinator basic functions."""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import datetime as dt
from hashlib import md5
import inspect
from operator import methodcaller
import os
from pathlib import Path
from pprint import pprint as pp
import sys
import time

import pandas as pd
from sqlalchemy import create_engine

from bripy.bllb.logging import setup_logging
from bripy.bllb.file import md5_blocks
from bripy.bllb.fs import get_stat, get_dir, rglob


LOG_ON = False
LOG_LEVEL = "DEBUG"
verbose = 2
OPT_MD5 = True
WORKERS = None
EXECUTOR = ThreadPoolExecutor
basepath = Path('..')
output = r'.\output.csv.gz'


def start_log(enable=True, lvl='WARNING'):
    log = setup_logging(enable, lvl, loguru_enqueue=True)  #, std_lib=True)
    log.info('examinator logging started')
    return log


def main():
    with EXECUTOR(max_workers=WORKERS) as executor:
        futures = executor.map(get_stat, rglob(basepath))
    results = [result for result in futures]
    df = pd.DataFrame(results)
    pp(df)
    print(df.info())
    engine = create_engine('sqlite:///output.db')
    df.to_sql('files', engine)

    elapsed = time.perf_counter() - s
    log.info(f"{__file__} executed in {elapsed:0.2f} seconds.".format())
    log.debug('\n\nFIN\n\n')


s = time.perf_counter()
log_on = LOG_ON
log_level = LOG_LEVEL
if verbose:
    log_on = True
    log_level = max(4 - verbose, 1) * 10
global log
log = start_log(log_on, log_level)
log.info(f'verbose: {verbose}')
log.warning(f"\nlogs enabled: {log_on}\nlog_level: {log_level}")
log.debug(f'Optional md5 hash: {OPT_MD5}')
time.sleep(0.05)  # Sleep to let logging initialize

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


# TODO:
## Recurse sub-directories
## create queue for directories to process
## multi-thread/process directories in queue
## read file timestamps
## persist file information to sqlite database
## queue files for hashing


# Ideas
## parse directory and file name information into key-value table
## fuzzy hashing
## metadata extraction
