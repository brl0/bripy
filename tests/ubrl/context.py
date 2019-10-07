#!/usr/bin/env python
"""Import ubrl module for tests."""

import os
import sys

lib_path = r"..\\ubrl"
lib_path_abs = os.path.abspath(
    os.path.join(os.path.dirname(__file__), lib_path))
sys.path.insert(0, lib_path_abs)

try:
    from ubrl import DNS, Server, URL  # noqa
except ImportError:
    from ubrl.ubrl import DNS, Server, URL  # noqa

lib_path = r"..\\ubrl\\bllb"
lib_path_abs = os.path.abspath(
    os.path.join(os.path.dirname(__file__), lib_path))
sys.path.insert(0, lib_path_abs)

from bllb import *  # noqa
from bllb_logging import *  # noqa
from bllb_file import *  # noqa
from bllb_str import *  # noqa

# from bllb_iter import *  # noqa


def main():
    """Testing."""
    logger = setup_logging()
    logger.info(sys.executable)
    logger.info(os.getcwd())
    logger.info(sys.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
