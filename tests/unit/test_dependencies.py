"""
测试 yai_nexus_api_middleware.dependencies 模块的单元测试。
"""
from fastapi import Request
from yai_nexus_api_middleware.dependencies import get_current_user, get_current_staff
from yai_nexus_api_middleware.models import UserInfo, StaffInfo


class TestGetCurrentUser:
    """测试 get_current_user 依赖项函数"""

    def test_获取当前用户_存在用户信息(self):
        """测试从请求状态中获取存在的用户信息"""
        # 创建模拟请求
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        user_info = UserInfo(tenant_id="tenant_123", user_id="user_456")
        request.state.user_info = user_info
        
        result = get_current_user(request)
        
        assert result is user_info
        assert result.tenant_id == "tenant_123"
        assert result.user_id == "user_456"

    def test_获取当前用户_不存在用户信息(self):
        """测试从请求状态中获取不存在的用户信息"""
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        # 不设置 user_info
        
        result = get_current_user(request)
        
        assert result is None

    def test_获取当前用户_用户信息为None(self):
        """测试从请求状态中获取值为None的用户信息"""
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        request.state.user_info = None
        
        result = get_current_user(request)
        
        assert result is None

    def test_获取当前用户_空用户信息(self):
        """测试从请求状态中获取空的用户信息"""
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        user_info = UserInfo()  # 空的用户信息
        request.state.user_info = user_info
        
        result = get_current_user(request)
        
        assert result is user_info
        assert result.tenant_id is None
        assert result.user_id is None


class TestGetCurrentStaff:
    """测试 get_current_staff 依赖项函数"""

    def test_获取当前员工_存在员工信息(self):
        """测试从请求状态中获取存在的员工信息"""
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        staff_info = StaffInfo(tenant_id="tenant_123", staff_id="staff_789")
        request.state.staff_info = staff_info
        
        result = get_current_staff(request)
        
        assert result is staff_info
        assert result.tenant_id == "tenant_123"
        assert result.staff_id == "staff_789"

    def test_获取当前员工_不存在员工信息(self):
        """测试从请求状态中获取不存在的员工信息"""
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        # 不设置 staff_info
        
        result = get_current_staff(request)
        
        assert result is None

    def test_获取当前员工_员工信息为None(self):
        """测试从请求状态中获取值为None的员工信息"""
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        request.state.staff_info = None
        
        result = get_current_staff(request)
        
        assert result is None

    def test_获取当前员工_空员工信息(self):
        """测试从请求状态中获取空的员工信息"""
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        staff_info = StaffInfo()  # 空的员工信息
        request.state.staff_info = staff_info
        
        result = get_current_staff(request)
        
        assert result is staff_info
        assert result.tenant_id is None
        assert result.staff_id is None


class TestDependenciesIntegration:
    """测试依赖项的集成场景"""

    def test_同一请求中获取用户和员工信息(self):
        """测试在同一个请求中同时获取用户和员工信息"""
        request = Request({"type": "http", "method": "GET", "url": "http://test.com/"})
        
        user_info = UserInfo(tenant_id="shared_tenant", user_id="user_123")
        staff_info = StaffInfo(tenant_id="shared_tenant", staff_id="staff_456")
        
        request.state.user_info = user_info
        request.state.staff_info = staff_info
        
        user_result = get_current_user(request)
        staff_result = get_current_staff(request)
        
        assert user_result is user_info
        assert staff_result is staff_info
        assert user_result.tenant_id == staff_result.tenant_id