from typing import Generic, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session


T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Base repository providing standard CRUD operations.
    Not ownership-aware - use OwnedResourceRepository for owned objects.

    This repository is useful for:
    - Non-owned objects (like NewsArticleORM)
    - Admin operations that bypass ownership checks
    - General CRUD operations where ownership is not required

    Type Parameters:
        T: The ORM model type this repository manages
    """

    def __init__(self, model: type[T], session: Session):
        """
        Initialize the repository.

        Args:
            model: The ORM model class this repository manages
            session: SQLAlchemy session for database operations
        """
        self.model = model
        self.session = session

    def get_by_id(self, id: int) -> T | None:
        """
        Get a single object by ID.

        Args:
            id: The primary key ID of the object

        Returns:
            The object if found, None otherwise
        """
        return self.session.get(self.model, id)

    def get_by_id_or_404(self, id: int) -> T:
        """
        Get object by ID or raise 404 if not found.

        Args:
            id: The primary key ID of the object

        Returns:
            The object if found

        Raises:
            HTTPException: 404 if object not found
        """
        obj = self.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )
        return obj

    def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """
        Get all objects with pagination.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            List of objects
        """
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.session.execute(statement).scalars().all())

    def create(self, obj: T) -> T:
        """
        Create a new object and commit to database.

        Args:
            obj: The object to create

        Returns:
            The created object with updated fields (like auto-generated ID)
        """
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: T) -> T:
        """
        Update an existing object and commit to database.

        Args:
            obj: The object to update (must already exist in session)

        Returns:
            The updated object with refreshed fields
        """
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        """
        Delete an object and commit to database.

        Args:
            obj: The object to delete
        """
        self.session.delete(obj)
        self.session.commit()

    def delete_by_id(self, id: int) -> None:
        """
        Delete an object by ID and commit to database.

        Args:
            id: The primary key ID of the object to delete

        Raises:
            HTTPException: 404 if object not found
        """
        obj = self.get_by_id_or_404(id)
        self.delete(obj)
