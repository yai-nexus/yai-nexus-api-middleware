from typing import List, Optional
from fastapi import FastAPI
from yai_nexus_api_middleware.internal.core_middleware import CoreMiddleware


class MiddlewareBuilder:
    """
    一个用于构建和配置 API 中间件栈的流式建造者。
    """

    def __init__(self, app: FastAPI):
        """
        初始化建造者，绑定到 FastAPI 应用实例。

        Args:
            app: 要应用中间件的 FastAPI 实例。
        """
        self._app = app
        
        # 中间件配置参数
        self._trace_header = "X-Trace-ID"
        self._tenant_id_header = "X-Tenant-ID"
        self._user_id_header = "X-User-ID"
        self._staff_id_header = "X-Staff-ID"
        self._log_exclude_paths = []
        
        # 启用标志
        self._tracing_enabled = False
        self._identity_enabled = False
        self._logging_enabled = False

    def with_tracing(self, header: str = "X-Trace-ID") -> "MiddlewareBuilder":
        """
        启用链路追踪功能。

        Args:
            header: 用于传递 trace_id 的请求头名称。

        Returns:
            返回建造者实例以支持链式调用。
        """
        self._tracing_enabled = True
        self._trace_header = header
        return self

    def with_identity_parsing(
        self,
        tenant_id_header: str = "X-Tenant-ID",
        user_id_header: str = "X-User-ID",
        staff_id_header: str = "X-Staff-ID",
    ) -> "MiddlewareBuilder":
        """
        启用身份解析功能。

        Args:
            tenant_id_header: 租户ID的请求头。
            user_id_header: 用户ID的请求头。
            staff_id_header: 员工ID的请求头。

        Returns:
            返回建造者实例以支持链式调用。
        """
        self._identity_enabled = True
        self._tenant_id_header = tenant_id_header
        self._user_id_header = user_id_header
        self._staff_id_header = staff_id_header
        return self

    def with_request_logging(
        self, exclude_paths: Optional[List[str]] = None
    ) -> "MiddlewareBuilder":
        """
        启用请求/响应日志记录功能。

        Args:
            exclude_paths: 不需要记录日志的路径列表。

        Returns:
            返回建造者实例以支持链式调用。
        """
        self._logging_enabled = True
        self._log_exclude_paths = exclude_paths or []
        return self

    def build(self):
        """
        构建并应用配置好的中间件到 FastAPI 应用。
        """
        # 添加核心中间件，包含所有功能
        self._app.add_middleware(
            CoreMiddleware,
            trace_header=self._trace_header,
            tenant_id_header=self._tenant_id_header,
            user_id_header=self._user_id_header,
            staff_id_header=self._staff_id_header,
            log_exclude_paths=self._log_exclude_paths,
            tracing_enabled=self._tracing_enabled,
            identity_enabled=self._identity_enabled,
            logging_enabled=self._logging_enabled,
        )
