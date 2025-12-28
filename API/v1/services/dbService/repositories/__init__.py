"""
Repository pattern for database operations with ownership validation.

This module provides:
- BaseRepository: Standard CRUD operations for non-owned objects
- OwnedResourceRepository: Ownership-validated CRUD for owned objects
- FastAPI dependency factories for automatic repository injection

Example Usage:
    from typing import Annotated
    from fastapi import Depends
    from services.dbService.repositories import get_feed_repository, OwnedResourceRepository
    from ORM.userFeedORM import UserFeedORM

    FeedRepo = Annotated[
        OwnedResourceRepository[UserFeedORM],
        Depends(get_feed_repository)
    ]

    @router.delete("/delete_feed/{feed_id}")
    def delete_feed(feed_id: int, repo: FeedRepo):
        repo.delete_owned(feed_id)
        return None
"""

from typing import TypeVar

from fastapi import Depends
from sqlalchemy.orm import Session

from ORM.ownedObjectMixin import OwnedObjectMixin
from ORM.userORM import UserORM
from services.authService.authService import get_current_active_user
from services.dbService.database import get_db

from .baseRepository import BaseRepository
from .ownedResourceRepository import OwnedResourceRepository


T = TypeVar("T", bound=OwnedObjectMixin)


def get_owned_repository(model: type[T]):
    """
    Factory function that returns a FastAPI dependency for owned resource repositories.

    This is a generic factory that can create repository dependencies for any
    OwnedObjectMixin subclass.

    Args:
        model: The ORM model class (must inherit from OwnedObjectMixin)

    Returns:
        A FastAPI dependency function that provides an OwnedResourceRepository

    Example:
        FeedRepository = Annotated[
            OwnedResourceRepository[UserFeedORM],
            Depends(get_owned_repository(UserFeedORM))
        ]

        @router.get("/feeds/{feed_id}")
        def get_feed(feed_id: int, repo: FeedRepository):
            feed = repo.get_owned_by_id_or_404(feed_id)
            return feed
    """

    def _get_repository(
        session: Session = Depends(get_db), current_user: UserORM = Depends(get_current_active_user)
    ) -> OwnedResourceRepository[T]:
        return OwnedResourceRepository(
            model=model, session=session, current_user_id=current_user.id
        )

    return _get_repository


def get_feed_repository(
    session: Session = Depends(get_db), current_user: UserORM = Depends(get_current_active_user)
) -> OwnedResourceRepository:
    """
    Pre-configured FastAPI dependency for UserFeed repository.

    This is a convenience dependency for the most common use case (UserFeedORM).
    Automatically injects the repository with the current user's session and ID.

    Returns:
        OwnedResourceRepository configured for UserFeedORM

    Example:
        from typing import Annotated
        from fastapi import Depends

        FeedRepo = Annotated[
            OwnedResourceRepository[UserFeedORM],
            Depends(get_feed_repository)
        ]

        @router.get("/feeds")
        def get_feeds(repo: FeedRepo):
            return repo.get_all_owned()
    """
    from ORM.userFeedORM import UserFeedORM

    return OwnedResourceRepository(
        model=UserFeedORM, session=session, current_user_id=current_user.id
    )


__all__ = [
    "BaseRepository",
    "OwnedResourceRepository",
    "get_owned_repository",
    "get_feed_repository",
]
