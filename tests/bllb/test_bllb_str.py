"""Tests for bllb logging module."""
# pylint: disable=unused-wildcard-import, undefined-variable

import re

from hypothesis import given
from hypothesis.strategies import text
from hypothesis_auto import auto_pytest, auto_pytest_magic
import pytest

try:
    from .context import *  # noqa
except ImportError:
    from context import *  # noqa

DEFAULT_RUNS = 50

FUNCTIONS = {
    hash_utf8: DEFAULT_RUNS,
    get_slug: DEFAULT_RUNS,
    date_slug: DEFAULT_RUNS,
    get_nums: DEFAULT_RUNS,
    get_ints: DEFAULT_RUNS,
    is_number: DEFAULT_RUNS,
    is_number_like: DEFAULT_RUNS,
    get_acronyms: DEFAULT_RUNS,
    split_camel_case: DEFAULT_RUNS,
    get_symbols: DEFAULT_RUNS,
    comp: DEFAULT_RUNS,
    comp_quick: DEFAULT_RUNS,
    comp_real_quick: DEFAULT_RUNS,
    symbol_counts_dist: DEFAULT_RUNS,
    check_case: DEFAULT_RUNS,
    keep_word: DEFAULT_RUNS,
    check_case_list: DEFAULT_RUNS,
    remove_chars: DEFAULT_RUNS,
    text_only: DEFAULT_RUNS,
    split_num_words: DEFAULT_RUNS,
    make_token_pattern: DEFAULT_RUNS,
    make_exp: DEFAULT_RUNS,
    pre: DEFAULT_RUNS,
    tok: DEFAULT_RUNS,
    rejoin: DEFAULT_RUNS,
    tok1: DEFAULT_RUNS,
    tok3: DEFAULT_RUNS,
    make_trans_table: DEFAULT_RUNS,
    get_whiteout: DEFAULT_RUNS,
    clean_text: DEFAULT_RUNS,
    pad_punctuation_w_space: DEFAULT_RUNS,
    Entropy.h: DEFAULT_RUNS,
    Entropy.h_printable: DEFAULT_RUNS,
    Entropy.h_alphanum_lower: DEFAULT_RUNS,
}

for func, runs in FUNCTIONS.items():
    auto_pytest_magic(func, auto_runs_=runs)


@given(text())
def test_split_words(text: str):
    """Test split_words function by performing identical steps."""
    new_s = " ".join(split_words(text, True))
    words = []
    for word in re.findall(r"[\w']+", text):
        for _ in word.split("_"):
            words.append(check_case(_, True))
    old_s = " ".join(words)
    assert new_s == old_s


@auto_pytest(test_split_words, auto_runs_=DEFAULT_RUNS)
def test_split_words_auto(test_case):
    """Auto generate tests for test_split_words."""
    test_case()


test_nums = ['0', '-1', '0.123', '.123', '-.123', '1.23']


@pytest.mark.parametrize("text", test_nums)
def test_is_number(text):
    """Test is_number."""
    assert is_number(text)


test_num_like = ['0', '-1,100', '1,23', '1/1/1', '1_100', '1.23.45.67']


@pytest.mark.parametrize("text", test_num_like)
def test_is_number_like(text):
    """Test is_number_like."""
    assert is_number_like(text)


def test_check_case():
    """Test check_case with non-default options."""
    assert check_case('TEST', lower=False) == 'TEST'


def test_token_num():
    """Test make_token_pattern with non-default options."""
    assert make_token_pattern(inc_num=True)


def test_pre():
    """Test pre with non-default options."""
    assert pre('TEST', casefold=False) == 'TEST'


def test_trans():
    """Test make_trans_table with non-default options."""
    assert make_trans_table(tolower=False, toupper=True, repl_num=True)
