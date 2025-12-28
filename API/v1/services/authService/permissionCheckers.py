from fastapi import Depends, HTTPException, status

from ORM.userORM import UserORM
from services.authService.authService import get_current_active_user


def require_permissions(required_permissions: list[str]):
    """
    Dependency to enforce that the current user has all required permissions (boolean/valueless).
    Usage:
        @router.get("/some-route", dependencies=[require_permissions(["GET.NEWS"])])
    """

    def permission_checker(current_user: UserORM = Depends(get_current_active_user)):
        # user.permissions assumed to be a dict: {permission_name: value}
        user_permissions = current_user.permissions or {}
        for perm in required_permissions:
            # Check if permission exists and has a value != -1 (valueless permissions)
            if perm not in user_permissions or user_permissions[perm] == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required permission missing or insufficient: {perm}",
                )
        return True

    return Depends(permission_checker)


def require_permission_with_max(permission_name: str, value_getter=None, min_value: int = 1):
    """
    Dependency to enforce that the current user has a numeric permission with at least `min_value`.
    - value_getter: a callable that receives current_user and returns the value to check
    - min_value: default minimum value if no value_getter is provided

    Usage:
        # static check
        @router.post("/write-feed", dependencies=[require_permission_with_max("WRITE.FEED", min_value=1)])

        # dynamic check against current state (e.g., number of feeds + 1)
        @router.post("/add_feed", dependencies=[require_permission_with_max(
            "ADD.FEED", value_getter=lambda user: len(user.feeds) + 1
        )])
    """

    def permission_checker(current_user: UserORM = Depends(get_current_active_user)):
        user_permissions = current_user.permissions or {}
        perm_value = user_permissions.get(permission_name)

        if perm_value is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission not found: {permission_name}",
            )

        # Determine the value to compare against
        check_value = value_getter(current_user) if value_getter else min_value

        if perm_value == -2:
            # Infinite permission
            return True
        if perm_value < check_value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission {permission_name} value insufficient ({perm_value} < {check_value})",
            )

        return True

    return Depends(permission_checker)
