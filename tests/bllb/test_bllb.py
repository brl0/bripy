#!/usr/bin/env python
"""Tests for bllb module."""
# pylint: disable=unused-wildcard-import, undefined-variable

import sys
import pytest
from scripttest import TestFileEnvironment as FileEnvironment

try:
    from .context import *  # noqa
except ImportError:
    from context import *  # noqa

env = FileEnvironment(ignore_hidden=False)

SCRIPT_PATH = r"..\..\ubrl\bllb\bllb.py"


def test_sysinfo():
    """Test that script has output."""
    res = env.run("python", SCRIPT_PATH, expect_stderr=True)
    assert sys.executable in res.stdout
    assert sys.version in res.stdout


def test_lines():
    """Test various line reading functions."""
    line1a = list(gen_lines(__file__))[0].split("\n")[0]
    line1b = get_lines(__file__, 0)[0]
    line1c = list(try_read(__file__))[0].split("\n")[0]
    assert line1a == line1b == line1c


def test_hash():
    """Test that hash of a known value works properly."""
    assert hash_utf8("") == "d41d8cd98f00b204e9800998ecf8427e"
