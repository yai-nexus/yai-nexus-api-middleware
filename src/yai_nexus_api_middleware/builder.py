from typing import List, Optional
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from yai_nexus_api_middleware.internal.handlers import MiddlewareHandlers
from .models import UserInfo, StaffInfo


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
        self._handlers = MiddlewareHandlers()

    def with_tracing(self, header: str = "X-Trace-ID") -> "MiddlewareBuilder":
        """
        启用链路追踪功能。

        Args:
            header: 用于传递 trace_id 的请求头名称。

        Returns:
            返回建造者实例以支持链式调用。
        """
        self._handlers.tracing_enabled = True
        self._handlers.trace_header = header
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
        self._handlers.identity_enabled = True
        self._handlers.tenant_id_header = tenant_id_header
        self._handlers.user_id_header = user_id_header
        self._handlers.staff_id_header = staff_id_header
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
        self._handlers.logging_enabled = True
        self._handlers.log_exclude_paths = set(exclude_paths or [])
        return self

    def build(self):
        """
        构建并应用配置好的中间件到 FastAPI 应用。
        """
        middleware = BaseHTTPMiddleware(
            app=self._app, dispatch=self._handlers.dispatch
        )
        self._app.add_middleware(BaseHTTPMiddleware, dispatch=self._handlers.dispatch)


# --- Dependency Injection ---

def get_current_user(request: Request) -> Optional[UserInfo]:
    """
    一个 FastAPI 依赖项，用于从请求状态中获取当前用户信息。
    """
    return getattr(request.state, "user_info", None)


def get_current_staff(request: Request) -> Optional[StaffInfo]:
    """
    一个 FastAPI 依赖项，用于从请求状态中获取当前员工信息。
    """
    return getattr(request.state, "staff_info", None) 