from collections.abc import Callable
from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ORM.ownedObjectMixin import OwnedObjectMixin

from .baseRepository import BaseRepository


T = TypeVar("T", bound=OwnedObjectMixin)


class OwnedResourceRepository(BaseRepository[T]):
    """
    Repository for objects that inherit from OwnedObjectMixin.
    Automatically enforces ownership validation on all operations.

    This is the PRIMARY interface for working with owned resources like UserFeedORM.
    All get/update/delete operations verify that the current user owns the object.

    Error Handling:
        - 404: Object doesn't exist
        - 403: Object exists but is not owned by current user

    Type Parameters:
        T: The ORM model type (must inherit from OwnedObjectMixin)
    """

    def __init__(self, model: type[T], session: Session, current_user_id: int):
        """
        Initialize the owned resource repository.

        Args:
            model: The ORM model class (must inherit OwnedObjectMixin)
            session: SQLAlchemy session
            current_user_id: ID of the current authenticated user
        """
        super().__init__(model, session)
        self.current_user_id = current_user_id

    def get_owned_by_id(self, id: int) -> T | None:
        """
        Get object by ID only if owned by current user.

        Args:
            id: The primary key ID of the object

        Returns:
            The object if found and owned by current user, None otherwise
            (returns None for both not-found AND not-owned cases)
        """
        obj = self.get_by_id(id)
        if obj and obj.is_owned_by(self.current_user_id):
            return obj
        return None

    def get_owned_by_id_or_404(self, id: int) -> T:
        """
        Get object by ID with ownership validation.

        This method distinguishes between "not found" and "not authorized":
        - Returns 404 if object doesn't exist
        - Returns 403 if object exists but is not owned by current user

        Args:
            id: The primary key ID of the object

        Returns:
            The object if found and owned by current user

        Raises:
            HTTPException: 404 if object not found
            HTTPException: 403 if object exists but not owned by user
        """
        obj = self.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )

        if not obj.is_owned_by(self.current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized to access this {self.model.__name__}",
            )

        return obj

    def get_all_owned(self, skip: int = 0, limit: int = 100) -> list[T]:
        """
        Get all objects owned by current user with pagination.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            List of objects owned by current user
        """
        statement = (
            select(self.model)
            .where(self.model.user_id == self.current_user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.execute(statement).scalars().all())

    def create_owned(self, obj: T) -> T:
        """
        Create a new object owned by current user.
        Automatically sets user_id to current user.

        Args:
            obj: The object to create (user_id will be set automatically)

        Returns:
            The created object with updated fields
        """
        obj.user_id = self.current_user_id
        return self.create(obj)

    def update_owned(self, id: int, update_fn: Callable[[T], None]) -> T:
        """
        Update an owned object with ownership validation.

        Args:
            id: Object ID
            update_fn: Callable that receives the object and applies updates

        Returns:
            Updated object

        Raises:
            HTTPException: 404 if not found
            HTTPException: 403 if not owned by user

        Example:
            def apply_updates(feed):
                feed.feedname = "New Name"
                feed.stocks = ["AAPL", "GOOGL"]

            updated_feed = repo.update_owned(feed_id, apply_updates)
        """
        obj = self.get_owned_by_id_or_404(id)
        update_fn(obj)
        return self.update(obj)

    def delete_owned(self, id: int) -> None:
        """
        Delete an owned object with ownership validation.

        Args:
            id: The primary key ID of the object to delete

        Raises:
            HTTPException: 404 if not found
            HTTPException: 403 if not owned by user
        """
        obj = self.get_owned_by_id_or_404(id)
        self.delete(obj)
