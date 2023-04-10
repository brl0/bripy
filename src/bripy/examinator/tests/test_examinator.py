#!/usr/bin/env python
"""Tests for `examinator` package."""

import unittest

from click.testing import CliRunner

from bripy.examinator.daskerator import main


class TestExaminator(unittest.TestCase):
    """Tests for `examinator` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        help_result = runner.invoke(main, ["--help"])
        assert help_result.exit_code == 0
        assert "Show this message and exit." in help_result.output
