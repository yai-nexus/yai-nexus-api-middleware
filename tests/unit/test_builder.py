"""
测试 yai_nexus_api_middleware.builder 模块的单元测试。
"""
from unittest.mock import Mock, patch
from fastapi import FastAPI
from yai_nexus_api_middleware.builder import MiddlewareBuilder


class TestMiddlewareBuilder:
    """测试 MiddlewareBuilder 类的功能"""

    def test_建造者初始化(self):
        """测试建造者的初始化"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        
        assert builder._app is app
        assert builder._trace_header == "X-Trace-ID"
        assert builder._tenant_id_header == "X-Tenant-ID"
        assert builder._user_id_header == "X-User-ID"
        assert builder._staff_id_header == "X-Staff-ID"
        assert builder._log_exclude_paths == []
        assert builder._tracing_enabled is False
        assert builder._identity_enabled is False
        assert builder._logging_enabled is False

    def test_启用追踪_默认参数(self):
        """测试启用追踪功能使用默认参数"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        
        result = builder.with_tracing()
        
        assert result is builder  # 支持链式调用
        assert builder._tracing_enabled is True
        assert builder._trace_header == "X-Trace-ID"

    def test_启用追踪_自定义参数(self):
        """测试启用追踪功能使用自定义参数"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        
        result = builder.with_tracing(header="X-Custom-Trace")
        
        assert result is builder
        assert builder._tracing_enabled is True
        assert builder._trace_header == "X-Custom-Trace"

    def test_启用身份解析_默认参数(self):
        """测试启用身份解析功能使用默认参数"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        
        result = builder.with_identity_parsing()
        
        assert result is builder
        assert builder._identity_enabled is True
        assert builder._tenant_id_header == "X-Tenant-ID"
        assert builder._user_id_header == "X-User-ID"
        assert builder._staff_id_header == "X-Staff-ID"

    def test_启用身份解析_自定义参数(self):
        """测试启用身份解析功能使用自定义参数"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        
        result = builder.with_identity_parsing(
            tenant_id_header="X-Custom-Tenant",
            user_id_header="X-Custom-User",
            staff_id_header="X-Custom-Staff"
        )
        
        assert result is builder
        assert builder._identity_enabled is True
        assert builder._tenant_id_header == "X-Custom-Tenant"
        assert builder._user_id_header == "X-Custom-User"
        assert builder._staff_id_header == "X-Custom-Staff"

    def test_启用请求日志_默认参数(self):
        """测试启用请求日志功能使用默认参数"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        
        result = builder.with_request_logging()
        
        assert result is builder
        assert builder._logging_enabled is True
        assert builder._log_exclude_paths == []

    def test_启用请求日志_自定义排除路径(self):
        """测试启用请求日志功能使用自定义排除路径"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        exclude_paths = ["/health", "/metrics", "/docs"]
        
        result = builder.with_request_logging(exclude_paths=exclude_paths)
        
        assert result is builder
        assert builder._logging_enabled is True
        assert builder._log_exclude_paths == exclude_paths

    def test_启用请求日志_None排除路径(self):
        """测试启用请求日志功能时排除路径为None"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        
        result = builder.with_request_logging(exclude_paths=None)
        
        assert result is builder
        assert builder._logging_enabled is True
        assert builder._log_exclude_paths == []

    def test_链式调用配置(self):
        """测试建造者模式的链式调用"""
        app = FastAPI()
        
        builder = (MiddlewareBuilder(app)
                  .with_tracing(header="X-Request-ID")
                  .with_identity_parsing(tenant_id_header="X-Tenant")
                  .with_request_logging(exclude_paths=["/health"]))
        
        assert builder._tracing_enabled is True
        assert builder._identity_enabled is True
        assert builder._logging_enabled is True
        assert builder._trace_header == "X-Request-ID"
        assert builder._tenant_id_header == "X-Tenant"
        assert builder._log_exclude_paths == ["/health"]

    @patch("yai_nexus_api_middleware.builder.CoreMiddleware")
    def test_构建中间件(self, mock_core_middleware):
        """测试构建和应用中间件"""
        app = FastAPI()
        app.add_middleware = Mock()  # 模拟 add_middleware 方法
        
        builder = (MiddlewareBuilder(app)
                  .with_tracing(header="X-Custom-Trace")
                  .with_identity_parsing(
                      tenant_id_header="X-Custom-Tenant",
                      user_id_header="X-Custom-User",
                      staff_id_header="X-Custom-Staff"
                  )
                  .with_request_logging(exclude_paths=["/health", "/metrics"]))
        
        builder.build()
        
        # 验证 add_middleware 被调用了一次
        app.add_middleware.assert_called_once()
        
        # 验证调用参数
        call_args = app.add_middleware.call_args
        assert call_args[0][0] is mock_core_middleware  # 第一个参数是中间件类
        
        # 验证关键字参数
        kwargs = call_args[1]
        assert kwargs["trace_header"] == "X-Custom-Trace"
        assert kwargs["tenant_id_header"] == "X-Custom-Tenant"
        assert kwargs["user_id_header"] == "X-Custom-User"
        assert kwargs["staff_id_header"] == "X-Custom-Staff"
        assert kwargs["log_exclude_paths"] == ["/health", "/metrics"]
        assert kwargs["tracing_enabled"] is True
        assert kwargs["identity_enabled"] is True
        assert kwargs["logging_enabled"] is True

    @patch("yai_nexus_api_middleware.builder.CoreMiddleware")
    def test_构建中间件_仅启用追踪(self, mock_core_middleware):
        """测试仅启用追踪功能时的构建"""
        app = FastAPI()
        app.add_middleware = Mock()
        
        builder = MiddlewareBuilder(app).with_tracing()
        builder.build()
        
        # 验证调用参数
        call_args = app.add_middleware.call_args
        kwargs = call_args[1]
        assert kwargs["tracing_enabled"] is True
        assert kwargs["identity_enabled"] is False
        assert kwargs["logging_enabled"] is False

    def test_建造者重复配置(self):
        """测试建造者重复配置的行为"""
        app = FastAPI()
        builder = MiddlewareBuilder(app)
        
        # 重复配置追踪
        builder.with_tracing(header="First-Header")
        builder.with_tracing(header="Second-Header")
        
        # 最后一次配置应该生效
        assert builder._trace_header == "Second-Header"
        assert builder._tracing_enabled is True