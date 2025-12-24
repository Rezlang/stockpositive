
from typing import List
from fastapi import Depends, HTTPException, status
from ORM.userORM import UserORM
from services.auth_service.auth_service import get_current_active_user


def require_permissions(required_permissions: List[str]):
    """
    Dependency to enforce that the current user has all required permissions.
    Usage:
        @router.get("/some-route", dependencies=[require_permissions(["perm1","perm2"])])
    """
    def permission_checker(current_user: UserORM = Depends(get_current_active_user)):
        user_permissions = set(current_user.permissions or [])
        if not set(required_permissions).issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required permissions: {required_permissions}"
            )
        return True
    return Depends(permission_checker)
