#!/usr/bin/env python
"""bllb - Brian L LiBrary."""

import sys

from bripy.bllb.bllb_logging import logger, DBG


def print_sysinfo():
    """Print Python version information."""
    print(f"exe:\t{sys.executable}\nversion:\t{sys.version}")


def setup_libtmux():
    import libtmux

    server = libtmux.Server()
    session = server.get_by_id("$0")
    window = session.attached_window
    return server, session, window


def main():
    print_sysinfo()
    return 0


if __name__ == "__main__":
    sys.exit(main())
