"""
简化的中间件集成测试。
专注于测试中间件的核心功能，不依赖复杂的日志文件验证。
"""
import tempfile
import os
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from typing import Optional

from yai_nexus_logger import LoggerConfigurator, init_logging, get_logger, trace_context
from yai_nexus_api_middleware import (
    MiddlewareBuilder,
    get_current_user,
    get_current_staff,
    UserInfo,
    StaffInfo,
    ApiResponse,
)


class TestSimpleMiddlewareIntegration:
    """简化的中间件集成测试"""

    def setup_method(self):
        """每个测试前的设置"""
        # 创建测试应用
        self.app = FastAPI(title="简化集成测试应用")
        
        # 配置中间件
        (
            MiddlewareBuilder(self.app)
                .with_tracing(header="X-Request-ID")
                .with_identity_parsing(
                    tenant_id_header="X-Tenant-ID",
                    user_id_header="X-User-ID",
                    staff_id_header="X-Staff-ID",
                )
                .with_request_logging(exclude_paths=["/health"])
                .build()
        )
        
        # 添加测试端点
        self._setup_test_endpoints()
        
        # 创建测试客户端
        self.client = TestClient(self.app)

    def _setup_test_endpoints(self):
        """设置测试端点"""
        
        @self.app.get("/", response_model=ApiResponse)
        async def read_root(user: Optional[UserInfo] = Depends(get_current_user)):
            if user and user.user_id:
                message = f"你好, 来自租户 {user.tenant_id} 的用户 {user.user_id}!"
            else:
                message = "你好, 匿名用户!"
            return ApiResponse.success(data={"message": message})

        @self.app.get("/staff", response_model=ApiResponse)
        async def read_staff(staff: Optional[StaffInfo] = Depends(get_current_staff)):
            if staff and staff.staff_id:
                message = f"你好, 来自租户 {staff.tenant_id} 的员工 {staff.staff_id}!"
            else:
                message = "你好, 匿名员工!"
            return ApiResponse.success(data={"message": message})

        @self.app.get("/error", response_model=ApiResponse)
        async def trigger_error():
            return ApiResponse.failure(code="TEST_ERROR", message="这是一个测试错误")

        @self.app.get("/trace")
        async def get_trace_info():
            current_trace = trace_context.get_trace_id()
            return {"trace_id": current_trace}

        @self.app.get("/health")
        async def health_check():
            return {"status": "ok"}

    def test_基本请求响应(self):
        """测试基本的请求响应功能"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "0"
        assert data["message"] == "操作成功"
        assert "你好, 匿名用户!" in data["data"]["message"]
        assert "trace_id" in data

    def test_自定义追踪ID(self):
        """测试自定义追踪ID的传递"""
        custom_trace_id = "test_trace_12345"
        headers = {"X-Request-ID": custom_trace_id}
        
        response = self.client.get("/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["trace_id"] == custom_trace_id
        
        # 验证响应头中也包含 trace_id
        assert response.headers.get("X-Trace-ID") == custom_trace_id

    def test_用户身份解析功能(self):
        """测试用户身份解析功能"""
        headers = {
            "X-Tenant-ID": "tenant_123",
            "X-User-ID": "user_456",
            "X-Request-ID": "identity_test_trace"
        }
        
        response = self.client.get("/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "来自租户 tenant_123 的用户 user_456" in data["data"]["message"]
        assert data["trace_id"] == "identity_test_trace"

    def test_员工身份解析功能(self):
        """测试员工身份解析功能"""
        headers = {
            "X-Tenant-ID": "tenant_789",
            "X-Staff-ID": "staff_abc",
            "X-Request-ID": "staff_test_trace"
        }
        
        response = self.client.get("/staff", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "来自租户 tenant_789 的员工 staff_abc" in data["data"]["message"]
        assert data["trace_id"] == "staff_test_trace"

    def test_错误响应处理(self):
        """测试错误响应功能"""
        response = self.client.get("/error")
        
        assert response.status_code == 200  # API 层面仍返回 200
        data = response.json()
        assert data["code"] == "TEST_ERROR"
        assert data["message"] == "这是一个测试错误"
        assert data["data"] is None
        assert "trace_id" in data

    def test_trace_context集成(self):
        """测试 trace_context 与中间件的集成"""
        custom_trace = "context_integration_test"
        headers = {"X-Request-ID": custom_trace}
        
        response = self.client.get("/trace", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["trace_id"] == custom_trace

    def test_健康检查端点(self):
        """测试健康检查端点（非ApiResponse格式）"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_并发请求处理(self):
        """测试并发请求的正确处理"""
        import concurrent.futures
        
        def make_request(trace_id: str):
            headers = {"X-Request-ID": trace_id}
            response = self.client.get("/", headers=headers)
            return response.json()["trace_id"]
        
        # 创建多个并发请求
        trace_ids = [f"concurrent_test_{i}" for i in range(5)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, tid) for tid in trace_ids]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证每个请求都返回了正确的 trace_id
        assert set(results) == set(trace_ids)

    def test_完整的用户会话流程(self):
        """测试完整的用户会话流程"""
        session_headers = {
            "X-Request-ID": "session_test_trace",
            "X-Tenant-ID": "session_tenant",
            "X-User-ID": "session_user"
        }
        
        # 访问根路径
        response1 = self.client.get("/", headers=session_headers)
        assert response1.status_code == 200
        assert "来自租户 session_tenant 的用户 session_user" in response1.json()["data"]["message"]
        
        # 获取trace信息
        response2 = self.client.get("/trace", headers=session_headers)
        assert response2.status_code == 200
        assert response2.json()["trace_id"] == "session_test_trace"
        
        # 所有响应都应该包含相同的trace_id
        assert response1.json()["trace_id"] == "session_test_trace"
        assert response2.json()["trace_id"] == "session_test_trace"

    def test_错误和成功响应的trace_id一致性(self):
        """测试错误和成功响应的trace_id一致性"""
        trace_id = "consistency_test_trace"
        headers = {"X-Request-ID": trace_id}
        
        # 成功响应
        success_response = self.client.get("/", headers=headers)
        assert success_response.json()["trace_id"] == trace_id
        
        # 错误响应
        error_response = self.client.get("/error", headers=headers)
        assert error_response.json()["trace_id"] == trace_id
        
        # 两个响应的trace_id应该一致
        assert success_response.json()["trace_id"] == error_response.json()["trace_id"]

    def test_混合身份信息处理(self):
        """测试同时包含用户和员工信息的请求"""
        headers = {
            "X-Request-ID": "mixed_identity_test",
            "X-Tenant-ID": "shared_tenant",
            "X-User-ID": "test_user",
            "X-Staff-ID": "test_staff"
        }
        
        # 用户端点应该获取用户信息
        user_response = self.client.get("/", headers=headers)
        assert "来自租户 shared_tenant 的用户 test_user" in user_response.json()["data"]["message"]
        
        # 员工端点应该获取员工信息
        staff_response = self.client.get("/staff", headers=headers)
        assert "来自租户 shared_tenant 的员工 test_staff" in staff_response.json()["data"]["message"]
        
        # 两个响应都应该有相同的trace_id
        assert user_response.json()["trace_id"] == staff_response.json()["trace_id"]

    def test_缺失身份信息的优雅处理(self):
        """测试缺失身份信息时的优雅处理"""
        # 只有部分身份信息
        partial_headers = {
            "X-Request-ID": "partial_identity_test",
            "X-Tenant-ID": "partial_tenant"
            # 缺少 X-User-ID 和 X-Staff-ID
        }
        
        user_response = self.client.get("/", headers=partial_headers)
        assert user_response.status_code == 200
        assert "匿名用户" in user_response.json()["data"]["message"]
        
        staff_response = self.client.get("/staff", headers=partial_headers)
        assert staff_response.status_code == 200
        assert "匿名员工" in staff_response.json()["data"]["message"]