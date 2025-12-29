from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class OAuthAccountORM(Base):
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    oauth_name = Column(String(100), nullable=False)
    access_token = Column(String(1024), nullable=False)
    expires_at = Column(Integer, nullable=True)
    refresh_token = Column(String(1024), nullable=True)
    account_id = Column(String(320), nullable=False)
    account_email = Column(String(320), nullable=True)

    user = relationship("UserORM", back_populates="oauth_accounts")