"""Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest


@pytest.fixture
def RANGES():
    yield [[*map(str, range(i))][::-1] for i in range(10)]
