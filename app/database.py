import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = Path(__file__).resolve().parent.parent

# Explicitly load .env so DATABASE_URL from .env is guaranteed to load
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DEFAULT_DB_PATH = BASE_DIR / "field_foresight.db"
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif DATABASE_URL.startswith("postgresql"):
    connect_args["connect_timeout"] = 3

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False, pool_pre_ping=True)
    with engine.connect() as conn:
        pass
except Exception:
    # Graceful fallback to SQLite for sandbox or offline environments
    DEFAULT_DB_PATH = BASE_DIR / "field_foresight.db"
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()