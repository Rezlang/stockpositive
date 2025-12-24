from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class UserFeedORM(Base):
    __tablename__ = "userfeeds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedname = Column(String(100), nullable=False)
    stocks = Column(ARRAY(String), nullable=False)
    sources = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    user = relationship("UserORM", back_populates="feeds")
