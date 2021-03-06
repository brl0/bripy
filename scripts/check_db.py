from sqlalchemy import create_engine
import pandas as pd

database = 'fileinfo.db'

engine = create_engine(f'sqlite:///{database}')
df = pd.read_sql('SELECT * FROM files;', engine)
print(df.info())
print(df.head())
