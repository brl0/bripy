#!/usr/bin/env python
"""bllb logging setup helper.

# TODO:
    # Set/change level functions
    # File output
"""

import logging
import sys
from typing import Optional, Union
from warnings import filterwarnings

import click

DEFAULT_LVL = "WARNING"
DISABLE_LVL = sys.maxsize

__all__ = ['setup_logging', 'disable_logging', 'logger', 'DBG']


def setup_logging(
        enable: bool = True,
        lvl: Optional[Union[int, str]] = None,
        std_lib: bool = False,
        loguru_enqueue: bool = True,
) -> object:
    """Enable or disable logging. Defaults to DEBUG level.

    Levels: {"DEBUG": 10, "INFO": 20, "WARNING": 30,
             "ERROR": 40, "CRITICAL": 50, "NOTSET" : 0}
    """
    #assert not (std_lib and loguru_enqueue)
    loguru_error = False
    if lvl is None:
        if enable:
            lvl = "DEBUG"
        else:
            lvl = DISABLE_LVL
    if not std_lib:
        try:
            if enable:
                logger = enable_loguru(lvl=lvl, enqueue=loguru_enqueue)
            else:
                logger = disable_loguru()
        except Exception as error:
            loguru_error = True
            print(error)
    if std_lib or loguru_error:
        if enable:
            logger = enable_std_logging(lvl=lvl)
            if loguru_error:
                logger.warning(
                    "Error importing loguru, using standard library logging.")
        else:
            logger = disable_std_logging()
    logger.debug(f"log settings\n"
                 f"\tEnabled:\t{enable}\n"
                 f"\tLevel:\t{lvl}\n"
                 f"\t{std_lib}")  # noqa
    return logger


def get_dbg(logger):
    if logger:
        if isinstance(logger, logging.Logger):
            return logger.debug
        return logger.opt(lazy=True).debug
    return print


def enable_loguru(name: str = "bllb",
                  lvl: Union[int, str] = "DEBUG",
                  enqueue: bool = True) -> object:
    """Enable loguru or return new loguru logger."""
    from loguru import logger

    logger.remove()
    logger.add(
        sys.stdout,
        level=lvl,
        colorize=True,
        format="<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        enqueue=enqueue,
    )
    logger.enable(name)
    logger.info(f"Imported loguru.\n\t Level: {lvl}\n\t enqueue: {enqueue}")
    filterwarnings("default")
    return logger


def disable_loguru(logger: Optional[object] = None) -> object:
    """Disable loguru logger or create and disable."""
    if isinstance(logger, logging.Logger):
        return disable_std_logging(logger)
    filterwarnings("ignore")
    if logger is None:
        from loguru import logger
    logger.disable("bllb")
    logger.remove()
    return logger


disable_logging = disable_loguru  # Will disable std if needed.


def enable_std_logging(name: str = "bllb",
                       lvl: Union[int, str] = "DEBUG") -> object:
    """Enable standard logging library, return logger."""
    log_format = "%(asctime)s : %(levelname)s \t: %(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(lvl)
    logging.disabled = False
    logging.disable(logging.NOTSET)
    logging.basicConfig(format=log_format, level=lvl)
    logger.info(f"Imported standard library logging module.\n\t Level: {lvl}")
    filterwarnings("default")
    return logger


def disable_std_logging(logger: Optional[object] = None) -> object:
    """Disable standard logging."""
    filterwarnings("ignore")
    if logger is None:
        logger = logging.getLogger("bllb")
    logging.disable(DISABLE_LVL)
    return logger


@click.command()
@click.option("--enable/--disable", default=True)
@click.option("--stdlib/--no-stdlib", default=False)
@click.option("--enqueue/--no-enqueue", default=False)
def main(enable: bool = True, stdlib: bool = False,
         enqueue: bool = False) -> int:
    """Testing."""
    logger = setup_logging(enable=enable,
                           lvl=None,
                           std_lib=stdlib,
                           loguru_enqueue=enqueue)
    logger.error("This is a logging configuration module.")
    disable_logging(logger)
    logger.error("Logging disabled.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
else:
    try:
        logger
    except Exception:
        logger = setup_logging(lvl=DEFAULT_LVL)
    DBG = get_dbg(logger)
