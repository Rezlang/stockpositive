from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2Token
from sqlmodel import Session, select

from models.token import Token
from models.user import UserCreate, UserResponse
from ORM.oauthAccountORM import OAuthAccountORM
from ORM.userORM import UserORM
from services.authService.authService import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_active_user,
    verify_password,
)
from services.authService.oauthConfig import google_oauth_client
from services.dbService.crud.userCrud import create_user, get_user_by_email, get_user_by_id
from services.dbService.database import get_db


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return create_user(db, user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and receive access token"""
    user = get_user_by_email(db, form_data.username)  # OAuth2 uses 'username' field
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user has a password (OAuth users might not have one)
    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses OAuth. Please sign in with Google or Apple.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserORM = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user


# OAuth2 Helper Functions
async def get_or_create_oauth_user(
    db: Session,
    oauth_name: str,
    access_token: str,
    account_id: str,
    account_email: str | None,
    expires_at: int | None = None,
    refresh_token: str | None = None,
) -> UserORM:
    """Get existing OAuth user or create a new one"""
    from ORM.userGroupORM import UserGroupORM

    # Check if OAuth account already exists
    statement = select(OAuthAccountORM).where(
        OAuthAccountORM.oauth_name == oauth_name,
        OAuthAccountORM.account_id == account_id
    )
    oauth_account = db.exec(statement).first()

    if oauth_account:
        # Update tokens
        oauth_account.access_token = access_token
        oauth_account.expires_at = expires_at
        oauth_account.refresh_token = refresh_token
        db.add(oauth_account)
        db.commit()
        db.refresh(oauth_account)
        return oauth_account.user

    # Check if user with this email already exists
    user = None
    if account_email:
        user = get_user_by_email(db, account_email)

    # Create new user if doesn't exist
    if not user:
        # Get default user group
        default_group = db.get(UserGroupORM, 3)
        if not default_group:
            default_group = UserGroupORM(name="default_users")
            db.add(default_group)
            db.commit()
            db.refresh(default_group)

        user = UserORM(
            usergroup_id=default_group.id,
            email=account_email or f"{account_id}@{oauth_name}.placeholder",
            username=None,
            hashed_password=None,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create OAuth account
    new_oauth_account = OAuthAccountORM(
        user_id=user.id,
        oauth_name=oauth_name,
        access_token=access_token,
        expires_at=expires_at,
        refresh_token=refresh_token,
        account_id=account_id,
        account_email=account_email,
    )
    db.add(new_oauth_account)
    db.commit()
    db.refresh(user)
    return user


# Google OAuth Routes
oauth2_authorize_callback = OAuth2AuthorizeCallback(
    google_oauth_client,
    redirect_url="http://localhost:8000/users/google/callback"
)


@router.get("/google/authorize")
async def google_authorize(request: Request):
    """Redirect to Google OAuth authorization page"""
    authorization_url = await google_oauth_client.get_authorization_url(
        redirect_uri="http://localhost:8000/users/google/callback",
        scope=["openid", "email", "profile"],
    )
    return RedirectResponse(url=authorization_url)


@router.get("/google/callback", response_model=Token)
async def google_callback(
    request: Request,
    access_token_state=Depends(oauth2_authorize_callback),
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    token: OAuth2Token = access_token_state[0]

    # Get user info from Google
    user_info = await google_oauth_client.get_id_email(token["access_token"])

    # Create or get user
    user = await get_or_create_oauth_user(
        db=db,
        oauth_name="google",
        access_token=token["access_token"],
        account_id=user_info[0],
        account_email=user_info[1],
        expires_at=token.get("expires_at"),
        refresh_token=token.get("refresh_token"),
    )

    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": jwt_token, "token_type": "bearer"}


# TODO: Apple OAuth Routes
# Apple OAuth requires additional setup and configuration
# Uncomment when Apple OAuth credentials are available
#
# from services.authService.oauthConfig import apple_oauth_client
#
# apple_oauth2_authorize_callback = OAuth2AuthorizeCallback(
#     apple_oauth_client,
#     redirect_url="http://localhost:8000/users/apple/callback"
# )
#
# @router.get("/apple/authorize")
# async def apple_authorize(request: Request):
#     """Redirect to Apple OAuth authorization page"""
#     authorization_url = await apple_oauth_client.get_authorization_url(
#         redirect_uri="http://localhost:8000/users/apple/callback",
#         scope=["name", "email"],
#     )
#     return RedirectResponse(url=authorization_url)
#
# @router.get("/apple/callback", response_model=Token)
# async def apple_callback(
#     request: Request,
#     access_token_state=Depends(apple_oauth2_authorize_callback),
#     db: Session = Depends(get_db)
# ):
#     """Handle Apple OAuth callback"""
#     token: OAuth2Token = access_token_state[0]
#     user_info = await apple_oauth_client.get_id_email(token["access_token"])
#
#     user = await get_or_create_oauth_user(
#         db=db,
#         oauth_name="apple",
#         access_token=token["access_token"],
#         account_id=user_info[0],
#         account_email=user_info[1],
#         expires_at=token.get("expires_at"),
#         refresh_token=token.get("refresh_token"),
#     )
#
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     jwt_token = create_access_token(
#         data={"sub": user.email},
#         expires_delta=access_token_expires
#     )
#
#     return {"access_token": jwt_token, "token_type": "bearer"}
