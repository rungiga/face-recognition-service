import os
import postgresql

DAT_HOST = os.environ.get('DAT_HOST', "localhost") 
DAT_PORT = os.environ.get('DAT_PORT', 5432) 
DB_USER = os.environ.get('DB_USER', "user") 
DB_PASSWORD = os.environ.get('DB_PASSWORD', "user") 
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'db')

def setup_db():
    db_url = f"pq://{DB_USER}:{DB_PASSWORD}@{DAT_HOST}:{DAT_PORT}/{POSTGRES_DB}"
    print(db_url)
    db = postgresql.open(db_url)
    db.execute("create extension if not exists cube;")
    db.execute("drop table if exists vectors")
    db.execute("create table vectors (id serial, label varchar, vec_low cube, vec_high cube);")
    db.execute("create index vectors_vec_idx on vectors (vec_low, vec_high);")

