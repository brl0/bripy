"""Test bllb df module."""
import pandas as pd

from bripy.bllb.df import pdhtml, pdinfo


def test_pdhtml(RANGES):
    """Simply execute function."""
    pdhtml(pd.DataFrame(RANGES))
    assert True


def test_pdinfo(RANGES):
    """Simply execute function."""
    pdinfo(pd.DataFrame(RANGES))
    assert True
