"""bllb iterator helpers."""
from collections.abc import Callable, Iterable
from functools import reduce
from operator import iconcat
from pprint import pprint
from typing import Any, List

from bripy.bllb.logging import DBG, logger


def flatten(lists: Iterable[Iterable[Any]]) -> list[Any]:
    """Recursively flatten nested lists."""
    return reduce(
        lambda res, x: res + (flatten(x) if isinstance(x, list) else [x]),
        lists,
        [],
    )


def reduce_iconcat(a: Iterable[Any]) -> list[Any]:
    """Concatenate and reduce iterable with functools."""
    return reduce(iconcat, a, [])


cat: Callable[[Iterable[str]], str] = "".join


def striter(
    iterable: Iterable[Any], item_delim: str = "\n", list_delim: str = "\n"
) -> str:
    """Concatenate items in an iterable into a string."""
    it = listerine(iterable)
    return item_delim.join(map(str, it)) + list_delim


def listerine(iterable: Iterable[Any]) -> list[Any]:
    """Wrap input into list."""
    it = iterable
    if isinstance(it, str):
        # wrap single string into list for proper handling
        it = [it]
        DBG("Wrapped str in list.")
    elif isinstance(it, set):
        # Sort unordered set into list
        it = sorted(it)
        DBG("Sorted set.")
    elif isinstance(it, dict):
        it = [*it.items()]
        DBG("Convert dict to list of tuples.")
    else:
        try:
            DBG("Trying to realize generators and expand iterator into list")
            it = [*it]
            DBG("Expansion worked.")
        except Exception as error:
            DBG(f"Expansion did not work. {error}")
            try:
                DBG("Trying to iterate directly.")
                it = [_ for _ in it]
                DBG("Iterating directly worked.")
            except Exception as error:
                DBG(f"Iterating directly did not work.  {error}")
                try:
                    DBG("Try casting to str and wrap in list.")
                    it = [str(it)]
                except Exception as error:
                    DBG("Unable to cast to str and wrap.  {error}")
                    DBG("Wrap individual item in list.")
                    it = [it]  # wrap any single objects in list
    return list(it)


def ppiter(iterable: Iterable[Any]):
    """Pretty print an iterable or other object."""
    print(f"type: {type(iterable)}")
    if isinstance(iterable, set):
        it = listerine(iterable)
    else:
        it = iterable
    try:
        length = len(it)
    except Exception as error:
        DBG(error)
        it = listerine(it)
        length = len(it)
    if length > 1:
        print(f"len: {length}\n")
    if isinstance(it, str):
        print(it)
    else:
        try:
            pprint(it)
        except Exception as error:
            logger.warning(f"iteration error: {error}")
            pprint(str(it))


def ppobj(obj: object) -> None:
    """Pretty print object.

    Does not print private dunder attributes."""
    for key in dir(obj):
        if str(key).startswith("__"):
            continue
        print("\n", key, ":")
        item = getattr(obj, key)
        if not item:
            continue
        if isinstance(item, str) or not len(item):
            pprint(item)
        else:
            pprint([*enumerate(item)])
