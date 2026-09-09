import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://review_bot:review_bot_dev_password@localhost:5432/review_bot",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Gives each request its own database session, and always closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
