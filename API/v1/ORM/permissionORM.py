from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class PermissionORM(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))

    usergroup_links = relationship(
        "UserGroupPermissionORM", back_populates="permission", cascade="all, delete-orphan"
    )
