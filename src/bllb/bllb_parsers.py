"""Various file parsers."""

from pathlib import Path
from typing import Optional
import click
import sys

try:
    from bllb_logging import *
except ImportError:
    from ubrl.bllb.bllb_logging import *


@click.group()
def main() -> int:  # pragma: no cover
    """Group commands."""
    return 0  # noqa


class HTML_Parser:
    """Class to hold HTML functions."""

    from bs4 import BeautifulSoup
    from bs4.element import Comment

    @classmethod
    def tag_visible(cls, element) -> bool:
        """
        Filter function to determine if element is visible.

        https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
        """
        if element.parent.name in [
                "style",
                "script",
                "head",
                "title",
                "meta",
                "[document]",
        ]:
            return False
        if isinstance(element, cls.Comment):
            return False  # pragma: no cover
        return True

    @classmethod
    def text_from_html(cls, body: str) -> str:
        """
        Extract text from visible elements in HTML document.

        https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
        """
        soup = cls.BeautifulSoup(body, "html.parser")
        texts = soup.findAll(text=True)
        texts = list(filter(cls.tag_visible, texts))
        return "\n".join(texts)


class PDF_Parser:
    """Class to hold PDF functions."""

    import PyPDF4

    @classmethod
    def text_from_pypdf4(cls, pdfFileObj) -> str:
        """Extract text using PyPDF4."""
        pdfReader = cls.PyPDF4.PdfFileReader(pdfFileObj)
        pdf_txt = ""
        for i in range(pdfReader.numPages):
            pageObj = pdfReader.getPage(i)
            pdf_txt += "\n" + pageObj.extractText()
        return pdf_txt


@main.command(help="Convert html to text.")
@click.option("--target", required=True, type=str)
def html2txt(target: str) -> str:
    """Cli command to convert html to text."""
    html = Path(target).read_text(errors="ignore")
    text = HTML_Parser.text_from_html(html)
    print(text)
    return text


@main.command(help="Convert pdf to text.")
@click.option("--target", required=True, type=str)
def pdf2txt(target: str) -> str:
    """Cli command to convert pdf to text."""
    with open(target, "rb") as pdf:
        text = PDF_Parser.text_from_pypdf4(pdf)
    print(text)
    return text


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
