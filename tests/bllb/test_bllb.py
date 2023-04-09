#!/usr/bin/env python
"""Tests for bllb module."""
# pylint: disable=unused-wildcard-import, undefined-variable

import sys

import pytest
from scripttest import TestFileEnvironment as FileEnvironment

from bripy.bllb.bllb import *

env = FileEnvironment(ignore_hidden=False)

SCRIPT_PATH = r"..\..\..\src\bripy\bllb\bllb.py"


def test_sysinfo():
    """Test that script has output."""
    res = env.run("python", SCRIPT_PATH, expect_stderr=True)
    assert sys.executable in res.stdout
    assert sys.version in res.stdout
