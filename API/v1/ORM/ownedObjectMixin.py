from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import declared_attr, relationship


if TYPE_CHECKING:
    pass


class OwnedObjectMixin:
    """
    Mixin for ORM models that belong to a user.
    Provides automatic ownership tracking and validation capabilities.

    Usage:
        class MyModel(Base, OwnedObjectMixin):
            __tablename__ = "mymodel"
            id = Column(Integer, primary_key=True)
            # user_id and user relationship are automatically added

    The mixin adds:
        - user_id: Foreign key to users table with index
        - user: Relationship to UserORM
        - is_owned_by(): Helper method for ownership checks
    """

    @declared_attr
    def user_id(cls):
        """Foreign key to the users table with index for query performance"""
        return Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    @declared_attr
    def user(cls):
        """Relationship to the UserORM"""
        # Use backref instead of back_populates to avoid conflicts
        # The UserORM can still define its own relationship with back_populates
        return relationship("UserORM", foreign_keys=[cls.user_id], viewonly=True)

    def is_owned_by(self, user_id: int) -> bool:
        """
        Check if this object is owned by the given user_id.

        Args:
            user_id: The ID of the user to check ownership against

        Returns:
            True if the object is owned by the user, False otherwise
        """
        return self.user_id == user_id
