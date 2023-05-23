from io import StringIO

import fsspec
import polars as pl


def pl_read_ndjson_fsspec(file):
    with fsspec.open(file, "rt", compression="infer") as f:
        data = f.read()
    data = StringIO(data)
    return pl.read_ndjson(data)


def unnest(df):
    """Unnest a dataframe with struct columns."""
    data = []
    for col, dtype in zip(df.columns, df.dtypes):
        if dtype != pl.Struct:
            data.append(df[col])
        else:
            fields = df[col].struct.fields
            rename_fields = [f"{col}_{f}" for f in fields]
            cols = (
                df[col]
                .struct.rename_fields(rename_fields)
                .to_frame()
                .unnest(col)
                .pipe(unnest)
                .get_columns()
            )
            data.extend(cols)
    return pl.DataFrame(data)
