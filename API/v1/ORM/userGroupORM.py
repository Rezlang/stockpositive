from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

# Association table
usergroup_permissions = Table(
    "usergroup_permissions",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("usergroup_id", Integer, ForeignKey("usergroups.id")),
    Column("permission_id", Integer, ForeignKey("permissions.id"))
)


class UserGroupORM(Base):
    __tablename__ = "usergroups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship(
        "PermissionORM",  # string reference avoids circular import
        secondary=usergroup_permissions,
        backref="usergroups"
    )
