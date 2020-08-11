#!/usr/bin/env python
"""bllb - Brian L LiBrary."""
import sys

from bripy.bllb.logging import logger, DBG


def setup_libtmux():
    """Connect to tmux instance."""
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
