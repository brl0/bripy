import re
import sys
from string import ascii_letters
from urllib.parse import scheme_chars

from fsspec.core import split_protocol, stringify_path, strip_protocol
from fsspec.utils import get_protocol, infer_storage_options

_SCHEME_BASE = rf"[{ascii_letters}]{scheme_chars}+:/?/?"
_SCHEME_STR = rf"^({_SCHEME_BASE})+"
_SCHEME_RE = re.compile(_SCHEME_STR)
_WIN_PATH_RE = re.compile(rf"^({_SCHEME_STR})*[{ascii_letters}]:[\\/]")


def posixify(path):
    """Stringify and convert separators to posix."""
    path = stringify_path(path)
    path = path.replace("\\", "/")
    return path


def is_win_drive_path(path):
    """Check if path contains a Windows drive letter."""
    return bool(_WIN_PATH_RE.match(stringify_path(path)))
