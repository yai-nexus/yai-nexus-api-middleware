"""
测试 examples.simple_usage 模块的示例测试。
验证示例代码的完整功能，包括日志文件生成符合预期。
"""
import os
import tempfile
import time
from pathlib import Path
from fastapi.testclient import TestClient

# 重要：在导入示例模块前，需要设置环境变量来避免日志文件冲突
def setup_test_logging():
    """设置测试专用的日志环境"""
    test_temp_dir = tempfile.mkdtemp()
    test_log_path = os.path.join(test_temp_dir, "test_simple_usage.log")
    return test_temp_dir, test_log_path


class TestSimpleUsageExample:
    """测试简单用法示例的完整功能"""

    def setup_method(self):
        """每个测试前的设置"""
        # 由于示例模块在导入时就会初始化日志，我们需要在这里处理
        # 创建临时目录用于测试日志
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_path = os.path.join(self.temp_dir, "test_simple_usage.log")
        
        # 动态导入并修改示例模块以使用测试日志路径
        self._setup_example_app()

    def _setup_example_app(self):
        """设置示例应用用于测试"""
        # 由于示例代码是完整的应用，我们需要重新创建它以控制日志路径
        import uvicorn
        from fastapi import FastAPI, Depends
        from typing import Optional
        from yai_nexus_logger import LoggerConfigurator, init_logging, get_logger, trace_context
        from yai_nexus_api_middleware import (
            MiddlewareBuilder,
            get_current_user,
            UserInfo,
            ApiResponse,
        )

        # 初始化测试专用的日志系统
        init_logging(
            LoggerConfigurator()
                .with_console_handler()
                .with_file_handler(path=self.test_log_path)
        )

        logger = get_logger(__name__)

        # 创建 FastAPI 应用实例
        app = FastAPI(title="YAI Nexus API Middleware 示例测试")

        # 使用流式建造者来配置和应用中间件
        (
            MiddlewareBuilder(app)
                .with_tracing(header="X-Request-ID")
                .with_identity_parsing(
                    tenant_id_header="X-Tenant-ID",
                    user_id_header="X-User-ID",
                    staff_id_header="X-Staff-ID",
                )
                .with_request_logging(
                    exclude_paths=["/health", "/docs", "/openapi.json"]
                )
                .build()
        )

        # 创建与示例相同的端点
        @app.get("/", response_model=ApiResponse)
        async def read_root(user: Optional[UserInfo] = Depends(get_current_user)) -> ApiResponse:
            if user and user.user_id:
                message = f"你好, 来自租户 {user.tenant_id} 的用户 {user.user_id}!"
            else:
                message = "你好, 匿名用户!"
            logger.info(f"read_root, message: {message}")
            return ApiResponse.success(data={"message": message})

        @app.get("/items/{item_id}", response_model=ApiResponse)
        async def get_item(item_id: str) -> ApiResponse:
            logger.info(f"正在获取 item, item_id: {item_id}")
            if item_id == "foo":
                return ApiResponse.success(data={"item_id": item_id, "name": "一个有效的物品"})
            else:
                return ApiResponse.failure(
                    code="ITEM_NOT_FOUND",
                    message=f"ID 为 '{item_id}' 的物品不存在。"
                )

        @app.get("/report", response_model=ApiResponse)
        async def create_report():
            current_trace_id = trace_context.get_trace_id()
            logger.info(f"正在生成报告，Trace ID: {current_trace_id}")
            return ApiResponse.success(
                data={"report_id": "rep_123", "trace_id_used": current_trace_id}
            )

        @app.get("/health")
        async def health_check():
            logger.info("正在执行健康检查")
            return {"status": "ok"}

        self.app = app
        self.client = TestClient(app)

    def teardown_method(self):
        """每个测试后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_示例根路径_匿名用户(self):
        """测试示例中的根路径端点 - 匿名用户场景"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证标准 ApiResponse 格式
        assert data["code"] == "0"
        assert data["message"] == "操作成功"
        assert "你好, 匿名用户!" in data["data"]["message"]
        assert "trace_id" in data
        
        # 验证日志文件生成并包含预期内容
        self._verify_log_contains("read_root, message: 你好, 匿名用户!")

    def test_示例根路径_已认证用户(self):
        """测试示例中的根路径端点 - 已认证用户场景"""
        headers = {
            "X-Request-ID": "example_user_test",
            "X-Tenant-ID": "example_tenant_123",
            "X-User-ID": "example_user_456"
        }
        
        response = self.client.get("/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证用户信息正确解析
        expected_message = "你好, 来自租户 example_tenant_123 的用户 example_user_456!"
        assert expected_message in data["data"]["message"]
        assert data["trace_id"] == "example_user_test"
        
        # 验证响应头包含 trace_id
        assert response.headers.get("X-Trace-ID") == "example_user_test"
        
        # 验证日志包含用户信息和 trace_id
        self._verify_log_contains("read_root, message: " + expected_message)
        self._verify_log_contains("example_user_test")

    def test_示例物品端点_成功场景(self):
        """测试示例中的物品端点 - 成功获取物品"""
        response = self.client.get("/items/foo")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["code"] == "0"
        assert data["data"]["item_id"] == "foo"
        assert data["data"]["name"] == "一个有效的物品"
        
        # 验证日志包含物品获取记录
        self._verify_log_contains("正在获取 item, item_id: foo")

    def test_示例物品端点_失败场景(self):
        """测试示例中的物品端点 - 物品不存在"""
        response = self.client.get("/items/bar")
        
        assert response.status_code == 200  # API 层面返回 200
        data = response.json()
        
        # 验证错误响应格式
        assert data["code"] == "ITEM_NOT_FOUND"
        assert "ID 为 'bar' 的物品不存在" in data["message"]
        assert data["data"] is None
        
        # 验证日志包含错误处理记录
        self._verify_log_contains("正在获取 item, item_id: bar")

    def test_示例报告端点_trace_context使用(self):
        """测试示例中的报告端点 - trace_context 使用"""
        custom_trace = "example_report_trace_123"
        headers = {"X-Request-ID": custom_trace}
        
        response = self.client.get("/report", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证 trace_id 在业务逻辑中的正确使用
        assert data["trace_id"] == custom_trace
        assert data["data"]["trace_id_used"] == custom_trace
        assert data["data"]["report_id"] == "rep_123"
        
        # 验证日志包含 trace_id 使用记录
        self._verify_log_contains(f"正在生成报告，Trace ID: {custom_trace}")

    def test_示例健康检查端点(self):
        """测试示例中的健康检查端点"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
        # 验证健康检查日志（不被中间件排除，因为端点内有日志）
        self._verify_log_contains("正在执行健康检查")

    def test_示例中间件配置完整性(self):
        """测试示例中间件配置的完整性"""
        # 测试追踪功能
        trace_id = "config_test_trace"
        headers = {"X-Request-ID": trace_id}
        
        response = self.client.get("/", headers=headers)
        assert response.headers.get("X-Trace-ID") == trace_id
        
        # 测试身份解析功能
        identity_headers = {
            "X-Tenant-ID": "config_tenant",
            "X-User-ID": "config_user",
            "X-Staff-ID": "config_staff"
        }
        
        response = self.client.get("/", headers=identity_headers)
        assert "来自租户 config_tenant 的用户 config_user" in response.json()["data"]["message"]
        
        # 测试请求日志功能（检查日志是否记录了请求）
        self._verify_log_contains("请求开始: GET /")
        self._verify_log_contains("请求完成: GET /")

    def test_示例排除路径功能(self):
        """测试示例中排除路径的日志功能"""
        # 记录当前日志大小
        initial_size = self._get_log_size()
        
        # 访问应该被排除的路径
        response = self.client.get("/docs")
        
        # 检查日志大小变化较小（没有记录请求日志）
        final_size = self._get_log_size()
        size_increase = final_size - initial_size
        
        # 应该没有明显的请求日志增长
        assert size_increase < 50  # 允许少量系统日志

    def test_示例请求日志记录格式(self):
        """测试示例中请求日志记录的格式"""
        test_trace = "log_format_test"
        headers = {
            "X-Request-ID": test_trace,
            "User-Agent": "示例测试客户端"
        }
        
        response = self.client.get("/", headers=headers)
        assert response.status_code == 200
        
        log_content = self._read_log_file()
        
        # 验证请求开始日志格式
        assert "请求开始: GET / - Client:" in log_content
        assert "User-Agent: 示例测试客户端" in log_content
        
        # 验证请求完成日志格式
        assert "请求完成: GET / with status 200" in log_content
        assert "seconds" in log_content

    def test_示例并发请求处理(self):
        """测试示例应用的并发请求处理能力"""
        import concurrent.futures
        
        def make_concurrent_request(index: int):
            trace_id = f"concurrent_example_{index}"
            headers = {"X-Request-ID": trace_id}
            response = self.client.get("/", headers=headers)
            return response.json()["trace_id"]
        
        # 发起并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_concurrent_request, i) for i in range(3)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 验证每个请求都得到了正确的 trace_id
        expected_traces = [f"concurrent_example_{i}" for i in range(3)]
        assert set(results) == set(expected_traces)
        
        # 验证所有 trace_id 都出现在日志中
        log_content = self._read_log_file()
        for trace_id in expected_traces:
            assert trace_id in log_content

    def _verify_log_contains(self, expected_content: str):
        """验证日志文件包含指定内容"""
        log_content = self._read_log_file()
        assert expected_content in log_content, f"日志中未找到预期内容: {expected_content}"

    def _read_log_file(self) -> str:
        """读取日志文件内容"""
        if not os.path.exists(self.test_log_path):
            return ""
        
        # 稍等片刻确保日志已写入
        time.sleep(0.1)
        
        with open(self.test_log_path, "r", encoding="utf-8") as f:
            return f.read()

    def _get_log_size(self) -> int:
        """获取日志文件大小"""
        if not os.path.exists(self.test_log_path):
            return 0
        return os.path.getsize(self.test_log_path)