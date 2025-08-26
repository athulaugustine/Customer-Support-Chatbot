from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

engine = create_engine("sqlite:///tickets.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)