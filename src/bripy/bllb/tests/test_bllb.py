#!/usr/bin/env python
"""Tests for bllb module."""
# pylint: disable=unused-wildcard-import, undefined-variable

import sys

from scripttest import TestFileEnvironment as FileEnvironment

env = FileEnvironment(ignore_hidden=False)

SCRIPT_PATH = "../../../py_info.py"


def test_sysinfo():
    """Test that script has output."""
    res = env.run(sys.executable, SCRIPT_PATH, expect_stderr=True)
    assert str(sys.executable) in res.stdout
    assert str(sys.version) in res.stdout
