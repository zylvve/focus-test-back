from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://user:password@db/postgres"
database = Database(DATABASE_URL)
Base = declarative_base()

engine = create_engine(DATABASE_URL)
