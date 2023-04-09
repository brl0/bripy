"""Test bllb.iter."""
from typing import List

import hypothesis.strategies as st
from conftest import DEFAULTS
from hypothesis import given
from hypothesis_auto import auto_pytest, auto_pytest_magic

from bripy.bllb.iter import *

# FUNCTIONS = {
#     striter: DEFAULTS.RUNS,
#     listerine: DEFAULTS.RUNS,
#     ppiter: DEFAULTS.RUNS,
# }

# for func, runs in FUNCTIONS.items():
#     auto_pytest_magic(func, auto_runs_=runs)

# auto_pytest_magic(striter, auto_runs_=DEFAULTS.RUNS)
# auto_pytest_magic(listerine, auto_runs_=DEFAULTS.RUNS)
# auto_pytest_magic(ppiter, auto_runs_=DEFAULTS.RUNS)


def test_flatten(RANGES):
    """Test len of flatten list matches sum of lens."""
    assert len(flatten(RANGES)) == sum(map(len, RANGES))


def test_reduce_iconcat(RANGES):
    """Test len of concatenated list matches sum of lens."""
    assert len(reduce_iconcat(RANGES)) == sum(map(len, RANGES))


def test_ppiter(RANGES):
    """Simply execute function."""
    ppiter(RANGES)
    assert True


@given(st.lists(st.text()))
def test_cat(strings: list[str]):
    """Test cat alias for join."""
    result = cat(strings)
    assert len(result) == sum(map(len, strings))
    assert result == "".join(strings)


@auto_pytest(test_cat, auto_runs_=DEFAULTS.RUNS)
def test_cat_auto(test_case):
    """Auto generate tests for test_cat."""
    test_case()


def test_listerine_str():
    """Test listerine with simple string."""
    assert listerine("abc") == ["abc"]
