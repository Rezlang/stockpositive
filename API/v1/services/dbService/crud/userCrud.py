
from fastapi import HTTPException
from sqlmodel import Session, or_, select

from models.user import UserCreate, UserUpdate
from ORM.userORM import UserORM
from services.authService.authService import get_password_hash


def get_user_by_email(session: Session, email: str) -> UserORM | None:
    statement = select(UserORM).where(UserORM.email == email)
    return session.exec(statement).first()


def get_user_by_username(session: Session, username: str) -> UserORM | None:
    statement = select(UserORM).where(UserORM.username == username)
    return session.exec(statement).first()


def get_user_by_phone(session: Session, phone_number: str) -> UserORM | None:
    statement = select(UserORM).where(UserORM.phone_number == phone_number)
    return session.exec(statement).first()


def get_user_by_identifier(session: Session, identifier: str) -> UserORM | None:
    """Get user by email, username, or phone number"""
    statement = select(UserORM).where(
        or_(
            UserORM.email == identifier,
            UserORM.username == identifier,
            UserORM.phone_number == identifier,
        )
    )
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: int) -> UserORM | None:
    return session.get(UserORM, user_id)


def create_user(session: Session, user: UserCreate) -> UserORM:
    from ORM.userGroupORM import UserGroupORM

    # Check if email exists
    if get_user_by_email(session, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username exists
    if get_user_by_username(session, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check if phone number exists (if provided)
    if user.phone_number and get_user_by_phone(session, user.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Get or create default user group (id=3 or create one)
    default_group = session.get(UserGroupORM, 3)
    if not default_group:
        # Create default user group if it doesn't exist
        default_group = UserGroupORM(name="default_users")
        session.add(default_group)
        session.commit()
        session.refresh(default_group)

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = UserORM(
        usergroup_id=default_group.id,
        email=user.email,
        username=user.username,
        phone_number=user.phone_number,
        hashed_password=hashed_password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(session: Session, user_id: int, user_update: UserUpdate) -> UserORM:
    db_user = get_user_by_id(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check for conflicts if updating email
    if user_update.email and user_update.email != db_user.email:
        if get_user_by_email(session, user_update.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        db_user.email = user_update.email

    # Check for conflicts if updating username
    if user_update.username and user_update.username != db_user.username:
        if get_user_by_username(session, user_update.username):
            raise HTTPException(status_code=400, detail="Username already taken")
        db_user.username = user_update.username

    # Check for conflicts if updating phone
    if user_update.phone_number and user_update.phone_number != db_user.phone_number:
        if get_user_by_phone(session, user_update.phone_number):
            raise HTTPException(status_code=400, detail="Phone number already registered")
        db_user.phone_number = user_update.phone_number

    # Update password if provided
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(session: Session, user_id: int) -> bool:
    db_user = get_user_by_id(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    session.commit()
    return True


def get_all_users(session: Session, skip: int = 0, limit: int = 100):
    statement = select(UserORM).offset(skip).limit(limit)
    return session.exec(statement).all()
