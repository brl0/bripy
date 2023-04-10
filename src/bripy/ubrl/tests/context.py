#!/usr/bin/env python
"""Import ubrl module for tests."""

import os
import sys

from bripy.ubrl.ubrl import DNS, URL, Server

# lib_path = r"..\\src\\ubrl"
# lib_path_abs = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), lib_path))
# sys.path.insert(0, lib_path_abs)


# lib_path = r"..\\ubrl\\bllb"
# lib_path_abs = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), lib_path))
# sys.path.insert(0, lib_path_abs)

# from bripy.bllb import *  # noqa
# from bripy.bllb.logging import *  # noqa
# from bripy.bllb.bllb_file import *  # noqa
# from bripy.bllb.str import *  # noqa

# from bripy.bllb.iter import *  # noqa


def main():
    """Testing."""
    logger = setup_logging()
    logger.info(sys.executable)
    logger.info(os.getcwd())
    logger.info(sys.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
