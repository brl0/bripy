#!/usr/bin/env python
"""bllb - Brian L LiBrary."""

import sys
import types

from bripy.bllb.bllb_logging import logger, DBG


def print_sysinfo():
    """Print Python version information."""
    print(f"exe:\t{sys.executable}\nversion:\t{sys.version}")


def has_version(m):
    """Check if module has version attribute."""
    try:
        if m.__version__:
            return True
    except Exception:
        pass
    try:
        if m.VERSION:
            return True
    except Exception:
        pass
    return False


def get_imports(context):
    """Create string list of imported modules.

    Only outputs modules that have conventional version attributes.
    """
    imports = [
        val.__name__
        for name, val in context.items()
        if isinstance(val, types.ModuleType) and has_version(val)
    ]
    imports = set(imports)
    imports = sorted(imports)
    imports = ",".join(imports)
    return imports


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
