from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class UserGroupPermissionORM(Base):
    __tablename__ = "usergroup_permissions"

    usergroup_id = Column(
        Integer, ForeignKey("usergroups.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id = Column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )

    # NULL = boolean / unlimited
    # INT  = constrained value (ex: WRITE.FEED limit)
    permission_value = Column(Integer, nullable=True)

    usergroup = relationship("UserGroupORM", back_populates="permission_links")
    permission = relationship("PermissionORM", back_populates="usergroup_links")
