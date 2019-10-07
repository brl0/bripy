"""Test bllb_iter."""

from typing import List

import pandas as pd

from hypothesis import given
import hypothesis.strategies as st
from hypothesis_auto import auto_pytest, auto_pytest_magic

try:
    from .context import *  # noqa
except ImportError:
    from context import *  # noqa

try:
    from ubrl.bllb.bllb_iter import *
except ImportError:
    from bllb_iter import *

DEFAULT_RUNS = 50
RANGES = [[*map(str, range(i))][::-1] for i in range(10)]

FUNCTIONS = {
    striter: DEFAULT_RUNS,
    listerine: DEFAULT_RUNS,
    ppiter: DEFAULT_RUNS,
    priter: DEFAULT_RUNS,
    pdinfo: DEFAULT_RUNS,
    ppriter: DEFAULT_RUNS,
}

for func, runs in FUNCTIONS.items():
    auto_pytest_magic(func, auto_runs_=runs)


def test_flatten():
    """Test len of flatten list matches sum of lens."""
    assert len(flatten(RANGES)) == sum(map(len, RANGES))


def test_reduce_iconcat():
    """Test len of concatenated list matches sum of lens."""
    assert len(reduce_iconcat(RANGES)) == sum(map(len, RANGES))


def test_priter_pandas():
    """Simply execute function."""
    assert priter(pd.DataFrame(RANGES))


def test_pdinfo():
    """Simply execute function."""
    assert pdinfo(pd.DataFrame(RANGES))


def test_pdhtml():
    """Simply execute function."""
    assert pdhtml(pd.DataFrame(RANGES))


@given(st.lists(st.text()))
def test_cat(strings: List[str]):
    """Test cat alias for join."""
    result = cat(strings)
    assert len(result) == sum(map(len, strings))
    assert result == "".join(strings)


@auto_pytest(test_cat, auto_runs_=DEFAULT_RUNS)
def test_cat_auto(test_case):
    """Auto generate tests for test_cat."""
    test_case()


def test_listerine_str():
    """Test listerine with simple string."""
    assert listerine('abc') == ['abc']
