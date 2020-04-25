#!/usr/bin/env python
"""bllb file helpers."""

from hashlib import md5
from itertools import islice
from pathlib import Path


from bripy.bllb.bllb_logging import logger, DBG


def gen_lines(filename: str):
    """Generate clean lines from txt."""
    with open(filename, "r", errors='ignore') as file:
        for line in file:
            yield line.splitlines()[0]


def get_lines(filename: str, line_num, count=1):
    """Get lines."""
    with open(filename, "r", errors='ignore') as file:
        return [
            _.splitlines()[0] for _ in islice(file, line_num, line_num + count)
        ]


def get_txt(filepath):
    """Get file as text."""
    with open(filepath, 'r', encoding="ISO-8859-1", errors='ignore') as file:
        return file.read()


def try_read(filename):  # pragma: no cover
    """Try to open file and read lines one at a time."""
    try:  # try to open
        with open(filename, "r", errors='ignore') as file:
            _ = True  # False
            try:  # try to get next line and print
                logger.debug("trying")
                while _:
                    yield next(file)
                    if _:
                        continue
                    else:
                        break
                else:
                    DBG("NOT True!?!")  # while else
                DBG("try complete")
            except Exception as error:  # try exception, may be done
                DBG("exception: ", error)
                # break
            else:  # except else, no errors
                DBG("no problems, except else")
            finally:  # done for each try
                DBG("finally")
                pass
    except Exception:  # error opening
        DBG("error opening")
        yield ''
        pass
    else:  # no error opening
        DBG("no error opening")
        pass
    finally:
        DBG("finally after try open")
        pass


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
        DBG(f'Item is a directory and will not be hashed.  {str(path)}')
        return
