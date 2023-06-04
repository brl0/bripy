from sqlalchemy import Column, MetaData, String, Table, create_engine

database = r"big_glob.db"

engine = create_engine(f"sqlite:///{database}")
metadata = MetaData()

files = Table("files", metadata, Column("path", String, index=True, primary_key=True))
metadata.create_all(engine)

for t in metadata.sorted_tables:
    print(t.name)
