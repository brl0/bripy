"""Entry point if module is executed with: ``python -m ubrl``."""

from .cli import main

try:  # noqa
    from bripy.ubrl.ubrl import DNS, URL, Server  # noqa
except ImportError:
    try:
        from ubrl.ubrl import DNS, URL, Server  # noqa
    except ImportError:
        from .ubrl import DNS, URL, Server  # noqa

if __name__ == "__main__":
    main()
