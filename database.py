import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 1. Dynamically connection arguments based on environment
db_connect_args = {}
if SQLALCHEMY_DATABASE_URL and "aivencloud.com" in SQLALCHEMY_DATABASE_URL:
    db_connect_args = {"ssl": {"ca": None}}

# 2. EnableConnection pool settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=db_connect_args, 
    pool_size=10,         
    max_overflow=20,      
    pool_recycle=1800     
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()