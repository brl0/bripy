"""Examinator basic functions."""

from bripy.bllb.file import md5_blocks
from bripy.bllb.fs import get_stat
from bripy.bllb.logging import setup_logging


OPT_MD5 = False
LOG_LEVEL = "WARNING"

def start_log(enable=True, lvl=LOG_LEVEL):
    logger = setup_logging(enable, lvl, loguru_enqueue=True)  #, std_lib=True)
    logger.info('examinator logging started')
    return logger

logger = start_log(False)
