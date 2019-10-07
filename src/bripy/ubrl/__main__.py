"""Entry point if module is executed with: ``python -m ubrl``."""

from .cli import main
from ubrl.ubrl import DNS, Server, URL  # noqa
from .ubrl import DNS, Server, URL  # noqa

if __name__ == "__main__":
    main()
