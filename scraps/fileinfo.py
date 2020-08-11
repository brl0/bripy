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
from bripy.bllb.str import hash_utf8

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


def md5_blocks(path, blocksize=1024 * 2048) -> str:
    path = Path(path)
    if not path.is_dir():
        try:
            hasher = md5()
            with path.open('rb') as file:
                block = file.read(blocksize)
                while len(block) > 0:
                    hasher.update(block)
                    block = file.read(blocksize)
            return hasher.hexdigest()
        except Exception as error:
            log.warning(
                f'Error trying to hash item: {str(path)}\nError:\n{error}')
            return
    else:
        log.debug(f'Item is a directory and will not be hashed.  {str(path)}')
        return


def get_stat(path, opt_md5=OPT_MD5, opt_pid=False) -> dict:
    log.debug(path)
    try:
        path = Path(path)
        info = dict([
            _ for _ in inspect.getmembers(path.lstat())
            if not _[0].startswith('_') and not inspect.isbuiltin(_[1])
        ])
        info.update(
            dict([(_[0], str(_[1])) for _ in inspect.getmembers(path)
                  if '__' not in _[0] and '<' not in str(_[1])]))
        info.update(
            dict([(str(_[0]), methodcaller(_[0])(path))
                  for _ in inspect.getmembers(path)
                  if _[0].startswith('is_') and _[0] != 'is_mount']))
        info['path'] = str(path)
        info['path_hash'] = hash_utf8(str(path))
        info['absolute_path'] = str(path.resolve())
        f_times = dict()
        for key, value in info.items():
            if key[-4:] == 'time':
                f_times[f'f_{key}'] = dt.datetime.fromtimestamp(value)
        info.update(f_times)
        if opt_md5:
            if not path.is_dir():
                try:
                    md5_hash = md5_blocks(path)
                    info['md5'] = md5_hash
                except:
                    log.warning(f'Could not hash item: {str(path)}')
            else:
                log.debug(
                    f'Item is a directory and will not be hashed.  {str(path)}'
                )
        if opt_pid:
            log.debug(
                f"working using OS pid: {os.getpid()}, opt_pid: {opt_pid}")
        return info
    except Exception as error:
        log.warning(error)
        return {'path': str(path), 'error': error}


def glob_paths(path):
    try:
        path = Path(path)
        if path.is_dir():
            return path.rglob('*')
        else:
            return path
    except Exception as error:
        log.warning(error)


def get_dir(d):
    path = Path(d)
    if path.is_dir():
        return [str(_) for _ in path.iterdir()]


def main():
    with EXECUTOR(max_workers=WORKERS) as executor:
        futures = executor.map(get_stat, glob_paths(basepath))
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
