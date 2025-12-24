from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from models.userFeed import UserFeedCreate, UserFeedResponse, UserFeedUpdate
from services.db_service.database import get_db
from services.auth_service.auth_service import get_current_active_user
from services.auth_service.permission_checkers import require_permissions, require_permission_with_max
from ORM.userFeedORM import UserFeedORM
from ORM.userORM import UserORM

router = APIRouter()


@router.post("/add_feed",
             response_model=UserFeedResponse,
             dependencies=[require_permission_with_max("ADD.FEED", value_getter=lambda u: len(u.feeds) + 1)])
def add_feed(
    feed_data: UserFeedCreate,
    current_user: UserORM = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    new_feed = UserFeedORM(
        user_id=current_user.id,
        feedname=feed_data.feedname,
        stocks=feed_data.stocks,
        sources=feed_data.sources
    )
    db.add(new_feed)
    db.commit()
    db.refresh(new_feed)
    return new_feed


@router.delete("/delete_feed/{feed_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[require_permissions(["DELETE.FEED"])])
def delete_feed(
    feed_id: int,
    current_user: UserORM = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    feed = db.get(UserFeedORM, feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    if feed.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this feed")

    db.delete(feed)
    db.commit()
    return None


@router.put("/edit_feed/{feed_id}",
            response_model=UserFeedResponse,
            dependencies=[require_permissions(["EDIT.FEED"])])
def edit_feed(
    feed_id: int,
    feed_update: UserFeedUpdate,
    current_user: UserORM = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    feed = db.get(UserFeedORM, feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    if feed.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to edit this feed")

    feed.feedname = feed_update.feedname or feed.feedname
    feed.stocks = feed_update.stocks or feed.stocks
    feed.sources = feed_update.sources or feed.sources

    db.add(feed)
    db.commit()
    db.refresh(feed)
    return feed


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
