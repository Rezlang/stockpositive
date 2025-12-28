import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlmodel import Session
from sqlalchemy import create_engine, event
from typing import Generator

# Add parent directory to path so we can import from the API package
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from services.dbService.database import get_db
from services.authService.authService import create_access_token, get_password_hash
from ORM.base import Base
from ORM.userORM import UserORM
from ORM.userGroupORM import UserGroupORM
from ORM.permissionORM import PermissionORM
from ORM.userGroupPermissionORM import UserGroupPermissionORM
from ORM.userFeedORM import UserFeedORM
from ORM.newsArticleORM import NewsArticleORM

# Test database URL - uses a separate test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/stockpositive_test"
)


@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    """Create a test database engine using PostgreSQL"""
    # Create engine for test database
    engine = create_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    Base.metadata.create_all(engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a test database session"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override"""
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> UserORM:
    """Create a test user with basic permissions"""
    from sqlmodel import select

    # Create a user group
    user_group = UserGroupORM(name="test_group")
    session.add(user_group)
    session.commit()
    session.refresh(user_group)

    # Get or create permissions
    permission_names = ["GET.NEWS", "GET.FEEDS", "ADD.FEED", "EDIT.FEED", "DELETE.FEED"]
    permissions = []

    for perm_name in permission_names:
        # Try to get existing permission
        statement = select(PermissionORM).where(PermissionORM.name == perm_name)
        existing_perm = session.exec(statement).first()

        if existing_perm:
            permissions.append(existing_perm)
        else:
            # Create new permission if it doesn't exist
            new_perm = PermissionORM(name=perm_name)
            session.add(new_perm)
            session.commit()
            session.refresh(new_perm)
            permissions.append(new_perm)

    # Link permissions to user group
    for perm in permissions:
        # ADD.FEED gets a max value of 5, others get None (unlimited)
        perm_value = 5 if perm.name == "ADD.FEED" else None
        ugp = UserGroupPermissionORM(
            usergroup_id=user_group.id,
            permission_id=perm.id,
            permission_value=perm_value
        )
        session.add(ugp)
    session.commit()

    # Create test user
    user = UserORM(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        usergroup_id=user_group.id
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session) -> UserORM:
    """Create an admin user with all permissions"""
    from sqlmodel import select

    # Create admin group
    admin_group = UserGroupORM(name="admin_group")
    session.add(admin_group)
    session.commit()
    session.refresh(admin_group)

    # Get or create admin permissions
    permission_names = ["LOAD.NEWS", "GET.NEWS", "GET.FEEDS", "ADMIN.GET.FEEDS", "ADD.FEED", "EDIT.FEED", "DELETE.FEED"]
    permissions = []

    for perm_name in permission_names:
        # Try to get existing permission
        statement = select(PermissionORM).where(PermissionORM.name == perm_name)
        existing_perm = session.exec(statement).first()

        if existing_perm:
            permissions.append(existing_perm)
        else:
            # Create new permission if it doesn't exist
            new_perm = PermissionORM(name=perm_name)
            session.add(new_perm)
            session.commit()
            session.refresh(new_perm)
            permissions.append(new_perm)

    # Link permissions to admin group
    for perm in permissions:
        # ADD.FEED gets a max value of 100, others get None (unlimited)
        perm_value = 100 if perm.name == "ADD.FEED" else None
        ugp = UserGroupPermissionORM(
            usergroup_id=admin_group.id,
            permission_id=perm.id,
            permission_value=perm_value
        )
        session.add(ugp)
    session.commit()

    # Create admin user
    admin = UserORM(
        username="adminuser",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        usergroup_id=admin_group.id
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    return admin


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: UserORM) -> dict:
    """Generate authentication headers for test user"""
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(name="admin_auth_headers")
def admin_auth_headers_fixture(admin_user: UserORM) -> dict:
    """Generate authentication headers for admin user"""
    access_token = create_access_token(data={"sub": admin_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(name="test_feed")
def test_feed_fixture(session: Session, test_user: UserORM) -> UserFeedORM:
    """Create a test feed for the test user"""
    feed = UserFeedORM(
        feedname="Test Feed",
        stocks=["AAPL", "MSFT", "GOOGL"],
        sources=["market"],
        user_id=test_user.id
    )
    session.add(feed)
    session.commit()
    session.refresh(feed)
    return feed
