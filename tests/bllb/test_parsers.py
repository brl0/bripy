"""Tests bllb parsers."""

from pathlib import Path

from click.testing import CliRunner
import dominate
from dominate.tags import *
import pytest

from fpdf import FPDF

try:
    from ubrl.bllb.bllb_parsers import (HTML_Parser, PDF_Parser, html2txt, pdf2txt)
except:
    from bllb_parsers import HTML_Parser, PDF_Parser, html2txt, pdf2txt

TEST_TEXT = 'This is test text.'


@pytest.fixture(scope="session")
def pdf_file(tmpdir_factory):
    """Create temp pdf file to test extraction."""
    fn = tmpdir_factory.mktemp("data").join("test.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, TEST_TEXT)
    pdf.output(fn, 'F')
    return fn


def test_parse_pdf(pdf_file):
    """Test parsing pdf file."""
    with open(pdf_file, "rb") as pdf:
        text = PDF_Parser.text_from_pypdf4(pdf)
    assert TEST_TEXT in text


@pytest.fixture(scope="session")
def html_file(tmpdir_factory):
    """Create temp html file to test extraction."""
    doc = dominate.document()
    with doc:
        with div():
            attr(cls='body')
            p(TEST_TEXT)
    fn = tmpdir_factory.mktemp("data").join("test.html")
    Path(fn).write_text(doc.render())
    return fn


def test_parse_html(html_file):
    """Test parsing HTML file."""
    html = Path(html_file).read_text(errors="ignore")
    text = HTML_Parser.text_from_html(html)
    assert TEST_TEXT in text


def test_html2txt(html_file):
    """Test html2txt command."""
    runner = CliRunner()
    result = runner.invoke(html2txt, [f"--target={str(html_file)}"])
    assert TEST_TEXT in result.output


def test_pdf2txt(pdf_file):
    """Test pdf2txt command."""
    runner = CliRunner()
    result = runner.invoke(pdf2txt, [f"--target={str(pdf_file)}"])
    assert TEST_TEXT in result.output
