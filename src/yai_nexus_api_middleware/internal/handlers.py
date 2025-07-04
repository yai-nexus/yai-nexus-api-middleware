import time
from typing import Callable, List, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from yai_nexus_api_middleware.models import UserInfo, StaffInfo
from yai_nexus_logger import get_logger, trace_context


class MiddlewareHandlers:
    """
    一个封装了所有中间件核心逻辑的内部类。
    Builder 将会配置这个类的一个实例，并最终将其包装成一个 FastAPI 中间件。
    """

    def __init__(
        self,
        trace_header: str = "X-Trace-ID",
        tenant_id_header: str = "X-Tenant-ID",
        user_id_header: str = "X-User-ID",
        staff_id_header: str = "X-Staff-ID",
        log_exclude_paths: List[str] = None,
    ):
        self.trace_header = trace_header
        self.tenant_id_header = tenant_id_header
        self.user_id_header = user_id_header
        self.staff_id_header = staff_id_header
        self.log_exclude_paths = set(log_exclude_paths or [])

        # 启用标志
        self.tracing_enabled = False
        self.identity_enabled = False
        self.logging_enabled = False
        self.logger = get_logger(__name__)

    async def _handle_tracing(self, request: Request):
        """处理链路追踪"""
        if not self.tracing_enabled:
            return
        trace_id = request.headers.get(self.trace_header)
        return trace_context.set_trace_id(trace_id)

    def _handle_identity(self, request: Request):
        """处理身份解析"""
        if not self.identity_enabled:
            return
        
        tenant_id = request.headers.get(self.tenant_id_header)
        request.state.user_info = UserInfo(
            tenant_id=tenant_id,
            user_id=request.headers.get(self.user_id_header),
        )
        request.state.staff_info = StaffInfo(
            tenant_id=tenant_id,
            staff_id=request.headers.get(self.staff_id_header),
        )

    async def _log_request(self, request: Request):
        """记录请求信息"""
        if not self.logging_enabled or request.url.path in self.log_exclude_paths:
            return

        self.logger.info(
            f"请求开始: {request.method} {request.url.path}",
            extra={
                "client": f"{request.client.host}:{request.client.port}",
                "user_agent": request.headers.get("user-agent", "Unknown"),
            },
        )

    async def _log_response(self, request: Request, response: Response, process_time: float):
        """记录响应信息"""
        if not self.logging_enabled or request.url.path in self.log_exclude_paths:
            return

        self.logger.info(
            f"请求完成: {request.method} {request.url.path}",
            extra={
                "status_code": response.status_code,
                "process_time_seconds": f"{process_time:.4f}",
            },
        )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        """
        统一的中间件调度函数。
        """
        start_time = time.time()
        
        # 按顺序执行：追踪 -> 身份 -> 日志
        token = await self._handle_tracing(request)
        self._handle_identity(request)
        await self._log_request(request)

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 将 trace_id 添加到响应头
            if self.tracing_enabled and trace_context.get_trace_id():
                response.headers["X-Trace-ID"] = trace_context.get_trace_id()
            
            await self._log_response(request, response, process_time)

        except Exception as e:
            process_time = time.time() - start_time
            self.logger.exception(
                f"请求异常: {request.method} {request.url.path}",
                extra={"process_time_seconds": f"{process_time:.4f}"},
            )
            raise e
        finally:
            if token:
                trace_context.reset_trace_id(token)

        return response 