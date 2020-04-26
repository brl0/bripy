# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for bripy.

    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""
import pytest


class DEFAULTS:
    RUNS = 1

@pytest.fixture
def RANGES():
    yield [[*map(str, range(i))][::-1] for i in range(10)]
