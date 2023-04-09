"""bllb string helpers."""
import hashlib
import math
import re
import string
from binascii import hexlify
from collections.abc import Collection, Iterator, Mapping
from datetime import datetime
from difflib import SequenceMatcher
from itertools import chain
from typing import Any, Dict, List
from unicodedata import normalize
from urllib.parse import quote_plus

from bripy.bllb.logging import DBG, logger


def hash_utf8(text: str) -> str:
    """Given utf8 string return md5 hash value as hex string."""
    hasher = hashlib.md5()
    hasher.update(text.encode("utf-8"))
    return hexlify(hasher.digest()).decode("utf-8")


def get_slug(text: str) -> str:
    """Sanitize string for file name, etc."""
    return quote_plus(normalize("NFKD", text)).replace("+", "_").casefold()


def date_slug(timestamp: datetime = datetime.now()) -> str:
    """Format current date stamp as a slug."""
    return timestamp.strftime("%Y%m%d%H%M%S")


def get_nums(text: str) -> list[float]:
    """Extract list of floats from a string."""
    numex = re.compile(r"\-?\.?\d+\.?\d*")
    return [float(_) for _ in numex.findall(str(text))]


def get_ints(text: str) -> list[int]:
    """Extract list of ints from string."""
    numex = re.compile(r"\-?\d+")
    return [int(_) for _ in numex.findall(str(text))]


def is_number(text: str) -> bool:
    """Check if string can be cast to float."""
    try:
        float(text)
        return True
    except ValueError:
        return False


def is_number_like(text: str) -> bool:
    """Check if string can be cast to float after removing punctuation."""
    try:
        float(remove_chars(text, r",._-)(][/\\"))
        return True
    except ValueError:
        return False


def get_acronyms(text: str) -> list[str]:
    """Extract uppercase only potential acronyms from string."""
    return [
        _
        for _ in text.translate(
            str.maketrans(string.ascii_lowercase, " " * len(string.ascii_lowercase))
        ).split()
        if len(_) > 1
    ]


def split_camel_case(text: str) -> str:
    """Split words written in camelCase."""
    return re.sub(
        r"(" r"(?<=[a-z])" r"[A-Z]|" r"(?<!\A)" r"[A-Z]" r"(?=[a-z])" r")", r" \1", text
    )


def get_symbols(text: str) -> str:
    """Extract only non-alpha-numeric symbols from string."""
    return text.translate(
        str.maketrans(
            string.ascii_letters + string.digits,
            " " * len(string.ascii_letters) + " " * len(string.digits),
        )
    )


def comp(text1: str, text2: str) -> float:
    """Compare two strings and return similarity ratio."""
    differ = SequenceMatcher(None, text1, text2)
    return differ.ratio()


def comp_quick(text1: str, text2: str) -> float:
    """Quick compare two strings and return similarity ratio."""
    differ = SequenceMatcher(None, text1, text2)
    return differ.quick_ratio()


def comp_real_quick(text1: str, text2: str) -> float:
    """Real quick compare two strings and return similarity ratio."""
    differ = SequenceMatcher(None, text1, text2)
    return differ.real_quick_ratio()


def symbol_counts_dist(
    texts: Collection[str], symbols: str = "`~!@#$%^&*)(-_+=|\\}{][:;><,.?"
) -> dict[str, dict[int, int]]:
    """Count distribution of symbols in strings."""
    import numpy as np

    return {
        ch: dict(
            zip(
                *np.unique(
                    list(map(lambda s: str(s).count(ch), texts)), return_counts=True
                )
            )
        )
        for ch in symbols
    }


class Entropy:
    """Class to hold functions for entropy.

    Entropy functions stolen from Ero Carrera.
    http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html
    """

    range_bytes = range(256)
    range_printable = (ord(c) for c in string.printable)
    range_alphanum_lower = (ord(c) for c in string.ascii_lowercase + string.digits)

    @staticmethod
    def h(data: bytes, iterator: Iterator = range_bytes) -> float:
        """Calculate entropy value."""
        if not data:
            return 0
        entropy = 0
        for x in iterator:
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += -p_x * math.log(p_x, 2)
        return entropy

    @classmethod
    def h_printable(cls, data: bytes) -> float:
        """Calculate entropy value of printable chars."""
        return cls.h(data, cls.range_printable)

    @classmethod
    def h_alphanum_lower(cls, data: bytes) -> float:
        """Calculate entropy value of alpha-numeric lowercase chars."""
        return cls.h(data, cls.range_alphanum_lower)


def check_case(text: str, lower: bool = True) -> str:
    """Pipeline function to standardize letter case."""
    if lower:
        return text.casefold()
    return text


def split_words(text: str, lower: bool = True) -> Iterator[str]:
    """Split words, check case, yield as iterator."""
    for word in re.findall(r"[\w']+", text):
        for _ in word.split("_"):
            yield check_case(_, lower)


def keep_word(word: str, req_len: int, stops: Collection[str]) -> bool:
    """Check if word meets keep criteria."""
    stops_set = set(stops)
    if word:
        if len(word) >= req_len:
            if word not in stops_set:
                if not is_number_like(word):
                    return True
    return False


def check_case_list(word_list: Collection[str], lower: bool = True) -> list[str]:
    """Check case of a list of words."""
    results = []
    for word in word_list:
        results.append(check_case(str(word), lower))
    return results


def remove_chars(text: str, chars: str = r"\\`*_{}[]()>#+-.!$", new: str = "") -> str:
    """Remove characters from a string."""
    for ch in chars:
        if ch in text:
            text = text.replace(ch, new)
    return text


def text_only(text: str) -> list[str]:
    """Extract only alphabet chars."""
    return re.findall(r"[" + string.ascii_letters + "']+", text)


def split_num_words(word_list: Collection[str], lower: bool = True) -> list[str]:
    """Split words containing numbers."""
    results = []
    if word_list:
        for text in word_list:
            if not text:
                break
            for word in re.findall(r"[\w']+", str(text)):
                if not word:  # pragma: no cover
                    break
                for _ in remove_chars(word, string.digits + "_", " ").split():
                    if not _:  # pragma: no cover
                        break
                    results.append(check_case(_, lower))
    return results


def make_token_pattern(
    ltr_cnt: int = 3, inc_num: bool = False, inc_apos: bool = True
) -> str:
    """Make token pattern."""
    chars = f"{string.ascii_letters}"
    if inc_num:
        chars += f"{string.digits}"
    if inc_apos:
        chars += "'"
    return rf"[{chars}]" r"{" rf"{ltr_cnt}" r",}"


def make_exp(ltr_cnt: int = 3, inc_num: bool = False, inc_apos: bool = True) -> Any:
    """Make compiled regular expression."""
    return re.compile(make_token_pattern(ltr_cnt, inc_num, inc_apos))


WORD_EXP = make_exp(3)

# Camel case word split expression
CAMEL_EXP = re.compile(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))")


def pre(text: str, casefold: bool = True, camel: bool = True) -> str:
    """Preprocessing of string prior to tokenization."""
    result = text
    if camel:
        result = CAMEL_EXP.sub(r" \1", result)
    result = normalize("NFKD", result)
    if casefold:
        return result.casefold()
    return result


MIN_WORD_LEN = 3


def tok(text: str, exp: Any = make_exp(MIN_WORD_LEN)) -> list[str]:
    """Tokenize string."""
    return exp.findall(text)


def rejoin(word_list: Collection[str], delim: str = " ") -> str:
    """Rejoin list of strings."""
    return str(delim).join(map(str, word_list))


WORD_EXP1 = make_exp(1)
WORD_EXP3 = make_exp(3)


def tok1(text: str) -> list[str]:
    """Tokenize allowing words of length 1 or greater."""
    return tok(text, WORD_EXP1)


def tok3(text: str) -> list[str]:
    """Tokenize allowing words of length 3 or greater."""
    return tok(text, WORD_EXP3)


def make_trans_table(
    tolower: bool = True,
    toupper: bool = False,
    repl_num: bool = False,
    repl_punc: bool = True,
    bad_chars: str = "",
) -> Mapping:
    """Create string translation table for translate string function."""
    good_chars = string.whitespace
    repl_chars = len(string.whitespace) * " "
    if tolower:
        good_chars += string.ascii_uppercase
        repl_chars += string.ascii_lowercase
    if toupper:
        good_chars += string.ascii_lowercase
        repl_chars += string.ascii_uppercase
    if repl_num:
        good_chars += string.digits
        repl_chars += len(string.digits) * " "
    if repl_punc:
        good_chars += string.punctuation
        repl_chars += len(string.punctuation) * " "
        good_chars += "–" + "—"
        repl_chars += " " + " "
        bad_chars += "®"
    return str.maketrans(good_chars, repl_chars, bad_chars)


def get_whiteout(nums: bool = True, chars: str = "", bad: str = "") -> Mapping:
    """Get string translate table to whiteout characters."""
    replace_chars = chars
    replace_chars += "?.,_-–—=+:;/\\"
    if nums:
        replace_chars += string.digits
    return str.maketrans(replace_chars, " " * len(replace_chars), bad)


PUNCTS = {
    ",",
    ".",
    '"',
    ":",
    ")",
    "(",
    "-",
    "!",
    "?",
    "|",
    ";",
    "'",
    "$",
    "&",
    "/",
    "[",
    "]",
    ">",
    "%",
    "=",
    "#",
    "*",
    "+",
    "\\",
    "•",
    "~",
    "@",
    "£",
    "·",
    "_",
    "{",
    "}",
    "©",
    "^",
    "®",
    "`",
    "<",
    "→",
    "°",
    "€",
    "™",
    "›",
    "♥",
    "←",
    "×",
    "§",
    "″",
    "′",
    "Â",
    "█",
    "½",
    "à",
    "…",
    "“",
    "★",
    "”",
    "–",
    "●",
    "â",
    "►",
    "−",
    "¢",
    "²",
    "¬",
    "░",
    "¶",
    "↑",
    "±",
    "¿",
    "▾",
    "═",
    "¦",
    "║",
    "―",
    "¥",
    "▓",
    "—",
    "‹",
    "─",
    "▒",
    "：",
    "¼",
    "⊕",
    "▼",
    "▪",
    "†",
    "■",
    "’",
    "▀",
    "¨",
    "▄",
    "♫",
    "☆",
    "é",
    "¯",
    "♦",
    "¤",
    "▲",
    "è",
    "¸",
    "¾",
    "Ã",
    "⋅",
    "‘",
    "∞",
    "∙",
    "）",
    "↓",
    "、",
    "│",
    "（",
    "»",
    "，",
    "♪",
    "╩",
    "╚",
    "³",
    "・",
    "╦",
    "╣",
    "╔",
    "╗",
    "▬",
    "❤",
    "ï",
    "Ø",
    "¹",
    "≤",
    "‡",
    "√",
}


def clean_text(text: str) -> str:
    """Remove punctuation and other characters from string."""
    result = str(text)
    for punct in PUNCTS:
        result = result.replace(punct, f" {punct} ")
    return result


def pad_punctuation_w_space(text: str) -> str:
    """Pad punctuation marks with space for separate tokenization."""
    result = re.sub(r'([:;"*.,!?()/\=-])', r" \1 ", text)
    result = re.sub(r"[^a-zA-Z]", " ", result)
    result = re.sub(r"\s{2,}", " ", result)
    # code for removing single characters
    result = re.sub(r"\b[a-zA-Z]\b", "", result)
    return result


stripper = lambda s: s.strip(string.whitespace + "\xa0")

fix_cr = lambda s: s.replace("\r\n", "\n").replace("\r", "\n")


def multisplit(w, splitters=["/", "\\", "_", " ", ".", ":"]):
    """Split word with multiple splitters."""
    words = [w]
    for s in splitters:
        words = [*chain(*[word.split(s) for word in words])]
    return [word for word in words if word]
