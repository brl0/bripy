"""Tests for bllb logging module."""
# pylint: disable=unused-wildcard-import, undefined-variable

import logging
import os
import sys
from warnings import filterwarnings

import pytest
from click.testing import CliRunner
from scripttest import TestFileEnvironment as FileEnvironment

from bripy.bllb.logging import disable_logging, disable_std_logging, main, setup_logging

try:
    import loguru
except ImportError:
    pass

SCRIPT_PATH = r"..\..\..\src\bripy\bllb\bllb_logging.py"
sys.path.insert(0, os.path.abspath(os.path.dirname(SCRIPT_PATH)))

ENV = FileEnvironment(ignore_hidden=False)
filterwarnings("ignore")


def test_loguru_logger(capsys):
    """Test loguru logger."""

    logger = setup_logging(
        enable=True, lvl="DEBUG", std_lib=False, loguru_enqueue=False
    )
    assert isinstance(logger, type(loguru.logger))

    msg = "Test loguru debug output."
    logger.debug(msg)
    captured = capsys.readouterr()
    assert msg in captured.out

    disable_logging(logger)
    disable_msg = "Test loguru disabled."
    captured = capsys.readouterr()
    assert disable_msg not in captured.out


def test_std_logger(caplog):
    """Test stdlib logger."""
    logger = setup_logging(enable=True, lvl=None, std_lib=True, loguru_enqueue=False)
    assert isinstance(logger, logging.Logger)

    msg = "Test logger debug output"
    logger.debug(msg)
    assert msg in caplog.text

    disable_logging(logger)
    disable_msg = "Test logger disabled"
    assert disable_msg not in caplog.text


def test_cli():
    """Test main function via cli."""
    res = ENV.run("python", SCRIPT_PATH, "--enable", expect_stderr=True)
    assert "loguru" in res.stdout


def test_cli_disable():
    """Test cli with disable produces no output."""
    res = ENV.run("python", SCRIPT_PATH, "--disable", expect_stderr=True)
    assert not res.stdout and not res.stderr


def test_cli_stdlib():
    """Test using stdlib."""
    res = ENV.run("python", SCRIPT_PATH, "--stdlib", expect_stderr=True)
    assert "standard" in res.stderr


def test_cli_stdlib_disable():
    """Test stdlib with disable."""
    res = ENV.run("python", SCRIPT_PATH, "--disable", "--stdlib", expect_stderr=True)
    assert not res.stdout and not res.stderr


def test_main():
    """Test main."""
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "This is a logging configuration module." in result.output


def test_main_disabled():
    """Test main with disable option."""
    runner = CliRunner()
    result = runner.invoke(main, ["--disable"])
    assert result.exit_code == 0
    assert result.output == ""


def test_main_std_disabled():
    """Test main with disable and stdlib options."""
    runner = CliRunner()
    result = runner.invoke(main, ["--disable", "--stdlib"])
    assert result.exit_code == 0
    assert result.output == ""


def test_loguru_disabled(capsys):
    """Test disable loguru."""
    logger = disable_logging()
    assert isinstance(logger, type(loguru.logger))
    msg = "Test loguru debug output."
    logger.debug(msg)
    captured = capsys.readouterr()
    assert not captured.out and not captured.err


def test_stdlib_disabled(capsys):
    """Test disable stdlib logging."""
    logger = disable_std_logging()
    assert isinstance(logger, logging.Logger)
    msg = "Test logging debug output."
    logger.debug(msg)
    captured = capsys.readouterr()
    assert not captured.out and not captured.err


def test_loguru_import_error():
    """Test fallback to stdlib if loguru raises exception."""

    class loguru:
        def __init__(self):
            raise Exception

    sys.modules["loguru"] = loguru
    logger = setup_logging()
    assert isinstance(logger, logging.Logger)
