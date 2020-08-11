"""DataFrame convenience functions."""
from io import StringIO
from typing import Optional

from IPython.core.display import HTML, display
import pandas as pd

from bripy.bllb.logging import logger, DBG


def pdhtml(df: pd.DataFrame, table_id: Optional[str] = 'table'):
    """Print/display Pandas DataFrame as HTML table (for Jupyter)."""
    #TODO: Check if in ipython/notebook
    try:
        display(
            HTML(pd.DataFrame(df).to_html(notebook=True, table_id=table_id)))
    except Exception as error:
        logger.error("Error displaying Pandas DataFrame as html: ", error)


def pdinfo(*dfs: pd.DataFrame, peek: Optional[int] = 3):
    """Display descriptive dataframe info."""
    if not dfs:
        return
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
        if len(df) >= 3 * peek:
            peek = min(len(df), peek)
            df_peek = pd.concat([df.head(peek), df.sample(peek), df.tail(peek)])
        else:
            df_peek = df
        pdhtml(df_peek, table_id=f'table_{idx}')
