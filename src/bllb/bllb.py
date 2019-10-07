#!/usr/bin/env python
"""bllb - Brian L LiBrary."""

import sys
import types

try:
    from bllb_logging import logger, DBG
except ImportError:
    try:
        from bllb.bllb_logging import logger, DBG
    except ImportError:
        from ubrl.bllb.bllb_logging import logger, DBG


def print_sysinfo():
    """Print Python version information."""
    print(f"exe:\t{sys.executable}\nversion:\t{sys.version}")


def has_version(val):
    """Check if module has version attribute."""
    try:
        if val.__version__:
            return True
    except Exception:
        return False
    return False


def get_imports(context):
    """Create list of imported modules as single string."""
    imports = [
        val.__name__
        for name, val in context.items()
        if isinstance(val, types.ModuleType) and has_version(val)
    ]
    imports = set(imports)
    imports = ",".join(sorted(imports))
    return imports


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
