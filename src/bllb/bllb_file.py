#!/usr/bin/env python
"""bllb file helpers."""

from itertools import islice

try:
    from bllb_logging import logger, DBG
except ImportError:
    try:
        from bllb.bllb_logging import logger, DBG
    except ImportError:
        from ubrl.bllb.bllb_logging import logger, DBG


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
                    logger.debug("NOT True!?!")  # while else
                logger.debug("try complete")
            except Exception as error:  # try exception, may be done
                logger.debug("exception: ", error)
                # break
            else:  # except else, no errors
                logger.debug("no problems, except else")
            finally:  # done for each try
                logger.debug("finally")
                pass
    except Exception:  # error opening
        logger.debug("error opening")
        yield ''
        pass
    else:  # no error opening
        logger.debug("no error opening")
        pass
    finally:
        logger.debug("finally after try open")
        pass
