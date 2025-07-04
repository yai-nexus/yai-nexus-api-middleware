"""
测试 yai_nexus_api_middleware.models 模块的单元测试。
"""
import pytest
from yai_nexus_api_middleware.models import UserInfo, StaffInfo


class TestUserInfo:
    """测试 UserInfo 模型的功能"""

    def test_用户信息创建_使用默认值(self):
        """测试创建空的用户信息对象"""
        user = UserInfo()
        assert user.tenant_id is None
        assert user.user_id is None

    def test_用户信息创建_使用完整参数(self):
        """测试创建完整的用户信息对象"""
        user = UserInfo(tenant_id="tenant_123", user_id="user_456")
        assert user.tenant_id == "tenant_123"
        assert user.user_id == "user_456"

    def test_用户信息创建_使用部分参数(self):
        """测试创建部分参数的用户信息对象"""
        user = UserInfo(tenant_id="tenant_123")
        assert user.tenant_id == "tenant_123"
        assert user.user_id is None

    def test_用户信息转换为字典(self):
        """测试用户信息对象转换为字典"""
        user = UserInfo(tenant_id="tenant_123", user_id="user_456")
        user_dict = user.model_dump()
        expected = {"tenant_id": "tenant_123", "user_id": "user_456"}
        assert user_dict == expected

    def test_用户信息从字典创建(self):
        """测试从字典创建用户信息对象"""
        data = {"tenant_id": "tenant_123", "user_id": "user_456"}
        user = UserInfo(**data)
        assert user.tenant_id == "tenant_123"
        assert user.user_id == "user_456"


class TestStaffInfo:
    """测试 StaffInfo 模型的功能"""

    def test_员工信息创建_使用默认值(self):
        """测试创建空的员工信息对象"""
        staff = StaffInfo()
        assert staff.tenant_id is None
        assert staff.staff_id is None

    def test_员工信息创建_使用完整参数(self):
        """测试创建完整的员工信息对象"""
        staff = StaffInfo(tenant_id="tenant_123", staff_id="staff_789")
        assert staff.tenant_id == "tenant_123"
        assert staff.staff_id == "staff_789"

    def test_员工信息创建_使用部分参数(self):
        """测试创建部分参数的员工信息对象"""
        staff = StaffInfo(staff_id="staff_789")
        assert staff.tenant_id is None
        assert staff.staff_id == "staff_789"

    def test_员工信息转换为字典(self):
        """测试员工信息对象转换为字典"""
        staff = StaffInfo(tenant_id="tenant_123", staff_id="staff_789")
        staff_dict = staff.model_dump()
        expected = {"tenant_id": "tenant_123", "staff_id": "staff_789"}
        assert staff_dict == expected

    def test_员工信息从字典创建(self):
        """测试从字典创建员工信息对象"""
        data = {"tenant_id": "tenant_123", "staff_id": "staff_789"}
        staff = StaffInfo(**data)
        assert staff.tenant_id == "tenant_123"
        assert staff.staff_id == "staff_789"