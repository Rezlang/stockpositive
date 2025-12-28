from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class UserGroupORM(Base):
    __tablename__ = "usergroups"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    permission_links = relationship(
        "UserGroupPermissionORM", back_populates="usergroup", cascade="all, delete-orphan"
    )

    # Optional convenience access
    permissions = relationship("PermissionORM", secondary="usergroup_permissions", viewonly=True)
