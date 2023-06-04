from pathlib import Path

import pandas as pd
from sqlalchemy import Column, MetaData, String, Table, create_engine, select
from sqlalchemy.exc import IntegrityError

basepath = r"C:\Users\b_r_l\OneDrive\Documents\code\python"
database = r"big_glob.db"

engine = create_engine(f"sqlite:///{database}")

if not Path(database).exists():
    metadata = MetaData()
    files = Table(
        "files", metadata, Column("path", String, index=True, primary_key=True)
    )
    metadata.create_all(engine)
else:
    metadata = MetaData(engine)
    files = Table("files", metadata, autoload=True, autoload_with=engine)

connection = engine.connect()

df = pd.read_sql("SELECT * FROM files;", engine)
print(df.info())
print(df.head())
