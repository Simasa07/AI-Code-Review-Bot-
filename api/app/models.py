from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from .database import Base


class Review(Base):
    """One row per Pull Request we've been asked to review."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    repo_full_name = Column(String, nullable=False)
    pr_number = Column(Integer, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending -> in_progress -> done / failed
    feedback = Column(String, nullable=True)  # the AI's review comments, once ready
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
