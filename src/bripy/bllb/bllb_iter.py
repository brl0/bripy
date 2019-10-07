#!/usr/bin/env python
"""bllb iterator helpers."""

from functools import reduce
from io import StringIO
from operator import iconcat
from pprint import pprint
from typing import Any, Callable, Iterable, List, Optional

from IPython.core.display import HTML, display
import pandas as pd

from bripy.bllb.bllb_logging import logger, DBG


def flatten(lists: Iterable[Iterable[Any]]) -> List[Any]:
    """Recursively flatten nested lists."""
    return reduce(
        lambda res, x: res + (flatten(x) if isinstance(x, list) else [x]),
        lists,
        [],
    )


def reduce_iconcat(a: Iterable[Any]) -> List[Any]:
    """Concatenate and reduce iterable with functools."""
    return reduce(iconcat, a, [])


cat: Callable[[Iterable[str]], str] = "".join


def striter(iterable: Iterable, item_delim: str = "\n",
            list_delim: str = "\n") -> str:
    """Concatenate items in an iterable into a string."""
    it = listerine(iterable)
    return item_delim.join(map(str, it)) + list_delim


def listerine(iterable: Iterable) -> List[Any]:
    """Wrap input into list."""
    it = iterable
    if isinstance(it, str):
        # wrap single string into list for proper handling
        it = [it]
        DBG('Wrapped str in list.')
    elif isinstance(it, set):
        # Sort unordered set into list
        it = sorted(it)
        DBG('Sorted set.')
    elif isinstance(it, dict):
        it = [*it.items()]
        DBG('Convert dict to list of tuples.')
    else:
        try:
            DBG('Trying to realize generators and expand iterator into list')
            it = [*it]
            DBG('Expansion worked.')
        except Exception:
            DBG('Expansion did not work.')
            try:
                DBG('Trying to iterate directly.')
                it = [_ for _ in it]
                DBG('Iterating directly worked.')
            except Exception:
                DBG('Iterating directly did not work.')
                try:
                    DBG('Try casting to str and wrap in list.')
                    it = [str(it)]
                except Exception:
                    DBG('Unable to cast to str and wrap.')
                    DBG('Wrap individual item in list.')
                    it = [it]  # wrap any single objects in list
    return list(it)


def ppiter(iterable: Iterable) -> bool:
    """Pretty print an iterable or other object."""
    logger.debug(f"type: {type(iterable)}")
    if isinstance(iterable, set):
        iterable = sorted(iterable)
    try:
        length = len(iterable)
    except Exception:
        iterable = listerine(iterable)
        length = len(iterable)
    if length > 1:
        print(f"len: {length}\n")
    pprint(iterable)


def priter(iterable: Iterable) -> bool:
    """Recursively print iterable."""
    try:
        if isinstance(iterable, pd.DataFrame):
            pdhtml(iterable)
            return True
    except Exception as error:
        logger.warning(f"Exception trying pdhtml: {error}")
        return False
    if isinstance(iterable, str):
        print(iterable)
    else:
        try:
            for i in iterable:
                try:
                    priter(i)
                except Exception as error:
                    logger.error(f"print error: {error}")
        except Exception:
            print(str(iterable))
    print()
    return True


def ppriter(iterable: Iterable) -> bool:
    """Pretty print an iterable or other object."""
    print(f"type: {type(iterable)}")
    if isinstance(iterable, pd.DataFrame):
        try:
            pdhtml(iterable)
            return True
        except Exception as error:
            logger.warning(f"Exception trying pdhtml: {error}")
            return False
    if isinstance(iterable, set):
        iterable = listerine(iterable)
    try:
        length = len(iterable)
    except Exception:
        iterable = listerine(iterable)
        length = len(iterable)
    if length > 1:
        print(f"len: {length}\n")
    if isinstance(iterable, str):
        print(iterable)
    else:
        try:
            pprint(iterable)
        except Exception as error:
            logger.error(f"pprint error: {error}")
            print(str(iterable))
    print()
    return True


def pdhtml(df: pd.DataFrame, table_id: Optional[str] = 'table') -> bool:
    """Print/display Pandas DataFrame as html table."""
    try:
        display(
            HTML(pd.DataFrame(df).to_html(notebook=True, table_id=table_id)))
        return True
    except Exception as error:
        logger.error("Error displaying Pandas DataFrame as html: ", error)
        return False


def pdinfo(*dfs: pd.DataFrame) -> bool:
    """Display descriptive dataframe info."""
    if not dfs:
        return False
    for idx, df in enumerate([*dfs]):
        if not isinstance(df, pd.DataFrame):
            try:
                df = pd.DataFrame(df)
                DBG('Converted object to DataFrame')
            except Exception as error:
                logger.warning('Not a DataFrame and could not convert.\n',
                               error)
                print(df)
                continue
        buffer = StringIO()
        df.info(buf=buffer, verbose=True, memory_usage='deep')
        print(buffer.getvalue())
        pdhtml(df.describe(), table_id=f'table_{idx}_desc')
        peek = min(len(df), 3)
        df_peek = pd.concat([df.head(peek), df.sample(peek), df.tail(peek)])
        pdhtml(df_peek, table_id=f'table_{idx}')
    return True
