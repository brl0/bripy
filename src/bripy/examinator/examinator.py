"""Examinator basic functions."""

import datetime as dt
from hashlib import md5
import inspect
from operator import methodcaller
import os
from pathlib import Path

from bripy.bllb.bllb_logging import setup_logging
from bripy.bllb.bllb_str import hash_utf8

OPT_MD5 = False
LOG_LEVEL = "WARNING"

def start_log(enable=True, lvl=LOG_LEVEL):
    logger = setup_logging(enable, lvl, loguru_enqueue=True)  #, std_lib=True)
    logger.info('examinator logging started')
    return logger


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
            logger.warning(
                f'Error trying to hash item: {str(path)}\nError:\n{error}')
            return
    else:
        logger.debug(f'Item is a directory and will not be hashed.  {str(path)}')
        return


def get_stat(path, opt_md5=OPT_MD5, opt_pid=False) -> dict:
    logger.debug(path)
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
                    logger.warning(f'Could not hash item: {str(path)}')
            else:
                logger.debug(
                    f'Item is a directory and will not be hashed.  {str(path)}'
                )
        if opt_pid:
            logger.debug(
                f"working using OS pid: {os.getpid()}, opt_pid: {opt_pid}")
        return info
    except Exception as error:
        logger.warning(error)
        return {'path': str(path), 'error': error}

logger = start_log(False)
