from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from models.userFeed import UserFeedCreate, UserFeedResponse, UserFeedUpdate
from ORM.userFeedORM import UserFeedORM
from ORM.userORM import UserORM
from services.authService.authService import get_current_active_user
from services.authService.permissionCheckers import require_permission_with_max, require_permissions
from services.dbService.database import get_db
from services.dbService.repositories import OwnedResourceRepository, get_feed_repository


router = APIRouter()

FeedRepo = Annotated[OwnedResourceRepository[UserFeedORM], Depends(get_feed_repository)]


@router.post(
    "/add_feed",
    response_model=UserFeedResponse,
    dependencies=[require_permission_with_max("ADD.FEED", value_getter=lambda u: len(u.feeds) + 1)],
)
def add_feed(feed_data: UserFeedCreate, repo: FeedRepo):
    new_feed = UserFeedORM(
        feedname=feed_data.feedname, stocks=feed_data.stocks, sources=feed_data.sources
    )
    return repo.create_owned(new_feed)


@router.delete(
    "/delete_feed/{feedId}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permissions(["DELETE.FEED"])],
)
def delete_feed(feedId: int, repo: FeedRepo):
    repo.delete_owned(feedId)
    return


@router.put(
    "/edit_feed/{feedId}",
    response_model=UserFeedResponse,
    dependencies=[require_permissions(["EDIT.FEED"])],
)
def edit_feed(feedId: int, feedUpdate: UserFeedUpdate, repo: FeedRepo):
    def applyUpdates(feed: UserFeedORM):
        feed.feedname = feedUpdate.feedname or feed.feedname
        feed.stocks = feedUpdate.stocks or feed.stocks
        feed.sources = feedUpdate.sources or feed.sources

    return repo.update_owned(feedId, applyUpdates)


@router.get(
    "/get_feeds",
    response_model=list[UserFeedResponse],
    dependencies=[require_permissions(["GET.FEEDS"])],
)
def get_user_feeds(current_user: UserORM = Depends(get_current_active_user)):
    """
    Get all feeds for the current user.
    """
    return current_user.feeds


@router.get(
    "/get_all_feeds",
    response_model=list[UserFeedResponse],
    dependencies=[require_permissions(["ADMIN.GET.FEEDS"])],
)
def get_all_feeds(db: Session = Depends(get_db)):
    """
    Get all feeds from all users. Requires ADMIN.GET.FEEDS permission.
    """

    feeds = db.exec(select(UserFeedORM)).all()
    return feeds
