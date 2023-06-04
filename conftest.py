import pytest


def pytest_addoption(parser):
    """Add command-line flags for pytest."""
    parser.addoption(
        "--skip-slow",
        action="store_true",
        help="skips slow tests",
        default=False,
    )
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,  # Only used for cli override
        help="run slow tests",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    skip_slow = pytest.mark.skip(reason="Skipping slow tests.")
    _slow = not config.getoption("--run-slow") and config.getoption(
        "--skip-slow",
    )
    for item in items:
        if _slow and "slow" in item.keywords:
            item.add_marker(skip_slow)
