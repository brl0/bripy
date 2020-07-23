
from datetime import datetime
import inspect
from operator import methodcaller
import os
from pathlib import Path

from fsspec import get_fs_token_paths
import pandas as pd

from bripy.bllb.file import md5_blocks, md5_blocks_fs
from bripy.bllb.str import hash_utf8, multisplit
from bripy.bllb.logging import logger, DBG


def get_stat(path, opt_md5=True) -> dict:
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
        return info
    except Exception as error:
        logger.warning(error)
        return {'path': str(path)}


def get_stat_fs(path, opt_md5=False) -> dict:
    DBG(path)
    fs, token, paths = get_fs_token_paths(path)
    protocol = get_protocol(fs)
    info = fs.info(path)
    info.update({"protocol": protocol})
    info.update({"created": pd.to_datetime(info["created"], unit="s")})
    info.update({"mtime": pd.to_datetime(info["mtime"], unit="s")})
    info.update({"words": set(multisplit(path))})
    if opt_md5:
        if not fs.isdir(path):
            try:
                md5_hash = md5_blocks_fs(path)
                info['md5'] = md5_hash
            except Exception as error:
                logger.warning(f'Could not hash item: {str(path)}\n{error}')
        else:
            DBG(
                f'Item is a directory and will not be hashed.  {str(path)}'
            )
    return info


def glob_paths(path, glob="*"):
    try:
        path = Path(path)
        if path.is_dir():
            return path.rglob(glob)
        else:
            return path
    except Exception as error:
        logger.warning(error)


def rglob(path):
    try:
        fs, token, paths = get_fs_token_paths(path)
        protocol = get_protocol(fs)
        if fs.isdir(path):
            return (f"{protocol}://{_}" for _ in fs.glob(Path(path)/'**'))
        return path
    except Exception as error:
        logger.warning(error)


def get_dir(d, glob="*"):
    path = Path(d)
    if path.is_dir():
        return path.glob(glob)


def get_dir_fs(d, glob="*"):
    fs, token, paths = get_fs_token_paths(d)
    protocol = get_protocol(fs)
    if fs.isdir(d):
        return [f"{protocol}://{_}" for _ in fs.glob(f"{d}/{glob}")]
    else:
        return []


def get_protocol(fs):
    return fs.protocol if isinstance(fs.protocol, str) else fs.protocol[0]


def is_dir(path):
    fs, token, paths = get_fs_token_paths(path)
    return fs.isdir(path)


def is_file(path):
    fs, token, paths = get_fs_token_paths(path)
    return fs.isfile(path)
