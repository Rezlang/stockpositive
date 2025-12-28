from sqlalchemy import ARRAY, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base
from .ownedObjectMixin import OwnedObjectMixin


class UserFeedORM(Base, OwnedObjectMixin):
    __tablename__ = "userfeeds"

    id = Column(Integer, primary_key=True, index=True)
    # user_id inherited from OwnedObjectMixin
    # user relationship overridden to add back_populates
    user = relationship("UserORM", back_populates="feeds", foreign_keys="UserFeedORM.user_id")
    feedname = Column(String(100), nullable=False)
    stocks = Column(ARRAY(String), nullable=False)
    sources = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
