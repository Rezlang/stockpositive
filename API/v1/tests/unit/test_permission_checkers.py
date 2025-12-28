from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from ORM.userORM import UserORM
from services.authService.permissionCheckers import require_permission_with_max, require_permissions


@pytest.mark.unit
class TestRequirePermissions:
    """Test the require_permissions dependency"""

    def test_require_permissions_with_valid_permission(self):
        """Test that user with valid permissions passes check"""
        # Create mock user with permissions
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"GET.NEWS": -1, "WRITE.NEWS": -1}

        # Get the checker function
        checker_dependency = require_permissions(["GET.NEWS"])
        # The return value is a Depends object, we need to get the dependency function
        checker_func = checker_dependency.dependency

        # Should not raise exception
        result = checker_func(current_user=mock_user)
        assert result is True

    def test_require_permissions_with_multiple_valid_permissions(self):
        """Test that user with multiple valid permissions passes check"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"GET.NEWS": -1, "WRITE.NEWS": -1, "DELETE.NEWS": -1}

        checker_dependency = require_permissions(["GET.NEWS", "WRITE.NEWS"])
        checker_func = checker_dependency.dependency

        result = checker_func(current_user=mock_user)
        assert result is True

    def test_require_permissions_with_missing_permission(self):
        """Test that user without required permission fails check"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"GET.NEWS": -1}

        checker_dependency = require_permissions(["WRITE.NEWS"])
        checker_func = checker_dependency.dependency

        with pytest.raises(HTTPException) as exc_info:
            checker_func(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "WRITE.NEWS" in exc_info.value.detail

    def test_require_permissions_with_zero_value_permission(self):
        """Test that permission with value 0 is considered insufficient"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"GET.NEWS": 0}

        checker_dependency = require_permissions(["GET.NEWS"])
        checker_func = checker_dependency.dependency

        with pytest.raises(HTTPException) as exc_info:
            checker_func(current_user=mock_user)

        assert exc_info.value.status_code == 403

    def test_require_permissions_with_no_permissions(self):
        """Test that user with no permissions fails check"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = None

        checker_dependency = require_permissions(["GET.NEWS"])
        checker_func = checker_dependency.dependency

        with pytest.raises(HTTPException) as exc_info:
            checker_func(current_user=mock_user)

        assert exc_info.value.status_code == 403

    def test_require_permissions_empty_list(self):
        """Test that empty permission list passes"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {}

        checker_dependency = require_permissions([])
        checker_func = checker_dependency.dependency

        result = checker_func(current_user=mock_user)
        assert result is True


@pytest.mark.unit
class TestRequirePermissionWithMax:
    """Test the require_permission_with_max dependency"""

    def test_permission_with_max_static_check_passes(self):
        """Test static permission check with sufficient value"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"WRITE.FEED": 10}

        checker_dependency = require_permission_with_max("WRITE.FEED", min_value=5)
        checker_func = checker_dependency.dependency

        result = checker_func(current_user=mock_user)
        assert result is True

    def test_permission_with_max_static_check_fails(self):
        """Test static permission check with insufficient value"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"WRITE.FEED": 3}

        checker_dependency = require_permission_with_max("WRITE.FEED", min_value=5)
        checker_func = checker_dependency.dependency

        with pytest.raises(HTTPException) as exc_info:
            checker_func(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "insufficient" in exc_info.value.detail.lower()

    def test_permission_with_max_dynamic_check_passes(self):
        """Test dynamic permission check with value_getter"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"ADD.FEED": 5}
        mock_user.feeds = [1, 2, 3]  # User has 3 feeds

        # User can add feed if they have less than 5 total
        checker_dependency = require_permission_with_max(
            "ADD.FEED", value_getter=lambda u: len(u.feeds) + 1
        )
        checker_func = checker_dependency.dependency

        result = checker_func(current_user=mock_user)
        assert result is True

    def test_permission_with_max_dynamic_check_fails(self):
        """Test dynamic permission check fails when limit exceeded"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"ADD.FEED": 3}
        mock_user.feeds = [1, 2, 3]  # User has 3 feeds, limit is 3

        checker_dependency = require_permission_with_max(
            "ADD.FEED", value_getter=lambda u: len(u.feeds) + 1
        )
        checker_func = checker_dependency.dependency

        with pytest.raises(HTTPException) as exc_info:
            checker_func(current_user=mock_user)

        assert exc_info.value.status_code == 403

    def test_permission_with_max_infinite_permission(self):
        """Test that -2 value means infinite permission"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"ADD.FEED": -2}
        mock_user.feeds = [1, 2, 3, 4, 5]  # Many feeds

        checker_dependency = require_permission_with_max(
            "ADD.FEED", value_getter=lambda u: len(u.feeds) + 1
        )
        checker_func = checker_dependency.dependency

        result = checker_func(current_user=mock_user)
        assert result is True

    def test_permission_with_max_missing_permission(self):
        """Test that missing permission raises exception"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = {"OTHER.PERMISSION": 10}

        checker_dependency = require_permission_with_max("ADD.FEED", min_value=1)
        checker_func = checker_dependency.dependency

        with pytest.raises(HTTPException) as exc_info:
            checker_func(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "not found" in exc_info.value.detail.lower()

    def test_permission_with_max_no_permissions(self):
        """Test that user with no permissions fails"""
        mock_user = Mock(spec=UserORM)
        mock_user.permissions = None

        checker_dependency = require_permission_with_max("ADD.FEED", min_value=1)
        checker_func = checker_dependency.dependency

        with pytest.raises(HTTPException) as exc_info:
            checker_func(current_user=mock_user)

        assert exc_info.value.status_code == 403
