import pandas as pd
from sqlalchemy import create_engine

output_db = r"fileinfo.db"
database = r"tracking.db"

engine = create_engine(f"sqlite:///{output_db}")
df = pd.read_sql("SELECT path FROM files;", engine)
tracking_engine = create_engine(f"sqlite:///{database}")
df.to_sql("files", tracking_engine)
print(df.info())
print(df.head())
