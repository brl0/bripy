"""Various file parsers."""

from pathlib import Path
import sys
from typing import Union

import click

from bripy.bllb.str import stripper, fix_cr

@click.group()
def main() -> int:  # pragma: no cover
    """Group commands."""
    return 0  # noqa

class HTML_Parser:
    """Class to hold HTML functions."""

    from bs4 import BeautifulSoup
    from bs4.element import Comment

    html_parsers = ['lxml', 'html5lib', 'html.parser']
    HTML_PARSER = html_parsers[0]

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
    def text_from_html(cls, body: Union[BeautifulSoup, str]) -> str:
        """
        Extract text from visible elements in HTML document.

        https://stackoverflow.com/questions/1936466
        """
        if isinstance(body, cls.BeautifulSoup):
            soup = body
        else:
            soup = cls.BeautifulSoup(body, cls.HTML_PARSER)
        texts = soup.findAll(text=True)
        texts = filter(cls.tag_visible, texts)
        texts = map(stripper, texts)
        texts = filter(len, texts)
        return "\n".join(texts)

    @classmethod
    def all_text(cls, body: Union[BeautifulSoup, str]) -> str:
        """Extract text from webpage.

        https://stackoverflow.com/questions/328356
        """
        if isinstance(body, cls.BeautifulSoup):
            soup = body
        else:
            soup = cls.BeautifulSoup(body, cls.HTML_PARSER)
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.replace_with("<br>")  # rip it out
        text = soup.get_text("<br>").replace('<br>', '\n')
        text = fix_cr(text)
        # Strip whitespace, including non-breaking spaces '\xa0'
        text = '\n'.join([stripper(line) for line in text.split('\n')
                          if stripper(line)])
        return text


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
