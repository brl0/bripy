from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

basepath = r'C:\Users\b_r_l\OneDrive\Documents\code\python'
database = r'big_glob.db'

engine = create_engine(f'sqlite:///{database}')

if not Path(database).exists():
    metadata = MetaData()
    files = Table('files', metadata,
                  Column('path', String, index=True, primary_key=True))
    metadata.create_all(engine)
else:
    metadata = MetaData(engine)
    files = Table('files', metadata, autoload=True, autoload_with=engine)

connection = engine.connect()


paths = ({'path': str(path)} for path in Path(basepath).rglob('*'))
for path in paths:
    try:
        connection.execute(files.insert(path))
        print(f'Inserted: {path}')
    except IntegrityError:
        print(f'Error: {path}')
