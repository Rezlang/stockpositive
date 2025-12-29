from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    usergroup_id = Column(Integer, ForeignKey("usergroups.id"), nullable=False)
    username = Column(String(50), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usergroup = relationship("UserGroupORM", backref="users")
    oauth_accounts = relationship("OAuthAccountORM", back_populates="user", cascade="all, delete-orphan")
    feeds = relationship("UserFeedORM", back_populates="user", cascade="all, delete-orphan")

    @property
    def permissions(self) -> dict[str, int | None]:
        """
        Returns:
        {
            "GET.NEWS": None,
            "WRITE.FEED": 5
        }
        """
        if not self.usergroup:
            return {}

        return {
            link.permission.name: link.permission_value for link in self.usergroup.permission_links
        }
