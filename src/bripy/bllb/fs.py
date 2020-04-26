
from datetime import datetime
import inspect
from operator import methodcaller
import os
from pathlib import Path

from bripy.bllb.file import md5_blocks
from bripy.bllb.bllb_str import hash_utf8
from bripy.bllb.logging import logger, DBG


def get_stat(path, opt_md5=True, opt_pid=False) -> dict:
    DBG(path)
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
                f_times[f'f_{key}'] = datetime.fromtimestamp(value)
        info.update(f_times)
        if opt_md5:
            if not path.is_dir():
                try:
                    md5_hash = md5_blocks(path)
                    info['md5'] = md5_hash
                except Exception as error:
                    logger.warning(f'Could not hash item: {str(path)}\n{error}')
            else:
                DBG(
                    f'Item is a directory and will not be hashed.  {str(path)}'
                )
        if opt_pid:
            DBG(
                f"working using OS pid: {os.getpid()}, opt_pid: {opt_pid}")
        return info
    except Exception as error:
        logger.warning(error)
        return {'path': str(path)}


def glob_paths(path):
    try:
        path = Path(path)
        if path.is_dir():
            return path.rglob('*')
        else:
            return path
    except Exception as error:
        logger.warning(error)


def get_dir(d):
    path = Path(d)
    if path.is_dir():
        return [str(_) for _ in path.iterdir()]
