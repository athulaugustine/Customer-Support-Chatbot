from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

# Ensure database file lives in ./data/tickets.db
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "tickets.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Auto-create tables if missing
Base.metadata.create_all(bind=engine)