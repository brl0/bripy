"""Test bllb file."""

from pathlib import Path

import pytest

from bripy.bllb.file import *

TEST_TEXT = "\n".join(
    [" ".join([*map(str, range(i))][::-1]) for i in range(10)]).strip()


@pytest.fixture(scope="session")
def tmp_file(tmpdir_factory):
    """Create temp file to test."""
    fn = tmpdir_factory.mktemp("data").join("test.txt")
    Path(fn).write_text(TEST_TEXT)
    return fn


def test_get_txt(tmp_file):
    """Test get_txt."""
    assert get_txt(tmp_file) == TEST_TEXT


def test_get_lines(tmp_file):
    """Test get_lines."""
    assert get_lines(tmp_file, 0, 2) == ['0', '1 0']


def test_gen_lines(tmp_file):
    """Test gen_lines."""
    assert TEST_TEXT == "\n".join(gen_lines(tmp_file))


def test_try_read(tmp_file):
    assert TEST_TEXT == "".join(try_read(tmp_file))
    assert [*try_read('')] == ['']


def test_lines():
    """Test various line reading functions."""
    line1a = list(gen_lines(__file__))[0].split("\n")[0]
    line1b = get_lines(__file__, 0)[0]
    line1c = list(try_read(__file__))[0].split("\n")[0]
    assert line1a == line1b == line1c
