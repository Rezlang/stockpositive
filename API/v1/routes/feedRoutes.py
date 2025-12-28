from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Annotated

from models.userFeed import UserFeedCreate, UserFeedResponse, UserFeedUpdate
from services.dbService.database import get_db
from services.authService.authService import get_current_active_user
from services.authService.permissionCheckers import require_permissions, require_permission_with_max
from services.dbService.repositories import get_feed_repository, OwnedResourceRepository
from ORM.userFeedORM import UserFeedORM
from ORM.userORM import UserORM

router = APIRouter()

FeedRepo = Annotated[
    OwnedResourceRepository[UserFeedORM],
    Depends(get_feed_repository)
]


@router.post("/add_feed",
             response_model=UserFeedResponse,
             dependencies=[require_permission_with_max("ADD.FEED", value_getter=lambda u: len(u.feeds) + 1)])
def add_feed(
    feed_data: UserFeedCreate,
    repo: FeedRepo
):
    new_feed = UserFeedORM(
        feedname=feed_data.feedname,
        stocks=feed_data.stocks,
        sources=feed_data.sources
    )
    return repo.create_owned(new_feed)


@router.delete("/delete_feed/{feed_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[require_permissions(["DELETE.FEED"])])
def delete_feed(
    feed_id: int,
    repo: FeedRepo
):
    repo.delete_owned(feed_id)
    return None


@router.put("/edit_feed/{feed_id}",
            response_model=UserFeedResponse,
            dependencies=[require_permissions(["EDIT.FEED"])])
def edit_feed(
    feed_id: int,
    feed_update: UserFeedUpdate,
    repo: FeedRepo
):
    def apply_updates(feed: UserFeedORM):
        feed.feedname = feed_update.feedname or feed.feedname
        feed.stocks = feed_update.stocks or feed.stocks
        feed.sources = feed_update.sources or feed.sources

    return repo.update_owned(feed_id, apply_updates)


@router.get("/get_feeds",
            response_model=List[UserFeedResponse],
            dependencies=[require_permissions(["GET.FEEDS"])])
def get_user_feeds(current_user: UserORM = Depends(get_current_active_user)):
    """
    Get all feeds for the current user.
    """
    return current_user.feeds


@router.get("/get_all_feeds", response_model=List[UserFeedResponse],
            dependencies=[require_permissions(["ADMIN.GET.FEEDS"])])
def get_all_feeds(db: Session = Depends(get_db)):
    """
    Get all feeds from all users. Requires ADMIN.GET.FEEDS permission.
    """

    feeds = db.exec(select(UserFeedORM)).all()
    return feeds
