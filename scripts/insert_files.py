from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData
from sqlalchemy import select
from sqlalchemy.sql import exists

basepath = r'C:\Users\b_r_l\OneDrive\Documents'
database = r'big_glob.db'

engine = create_engine(f'sqlite:///{database}')
connection = engine.connect()

metadata = MetaData(engine)

files = Table('files', metadata, autoload=True, autoload_with=engine)

for path in Path(basepath).iterdir():
    stmt = select([files]).where(files.c.path == str(path))
    result = connection.execute(stmt)
    row = result.fetchone()
    if not row:
        connection.execute(files.insert({'path': str(path)}))
        print(f'Inserted: {path}')
    else:
        print(f'Existing: {path}')
