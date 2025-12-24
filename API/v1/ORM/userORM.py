from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    usergroup_id = Column(Integer, ForeignKey("usergroups.id"), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String(20), nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    usergroup = relationship(
        "UserGroupORM", backref="users")  # string reference

    @property
    def permissions(self):
        if self.usergroup and self.usergroup.permissions:
            return [p.name for p in self.usergroup.permissions]
        return []
