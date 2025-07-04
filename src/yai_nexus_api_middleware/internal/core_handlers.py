import time
from typing import List, Optional, Callable, Awaitable  

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from yai_nexus_logger import get_logger, trace_context

from yai_nexus_api_middleware.models import StaffInfo, UserInfo


class CoreMiddleware(BaseHTTPMiddleware):
    """
    核心中间件类，处理链路追踪、身份解析和请求日志记录。
    """

    def __init__(
        self,
        app,
        trace_header: str = "X-Trace-ID",
        tenant_id_header: str = "X-Tenant-ID",
        user_id_header: str = "X-User-ID",
        staff_id_header: str = "X-Staff-ID",
        log_exclude_paths: Optional[List[str]] = None,
        tracing_enabled: bool = False,
        identity_enabled: bool = False,
        logging_enabled: bool = False,
    ):
        super().__init__(app)
        self.trace_header = trace_header
        self.tenant_id_header = tenant_id_header
        self.user_id_header = user_id_header
        self.staff_id_header = staff_id_header
        self.log_exclude_paths = set(log_exclude_paths or [])
        
        # 启用标志
        self.tracing_enabled = tracing_enabled
        self.identity_enabled = identity_enabled
        self.logging_enabled = logging_enabled
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
            f"请求开始: {request.method} {request.url.path} - Client: %s, User-Agent: %s",
            f"{request.client.host}:{request.client.port}",
            request.headers.get("user-agent", "Unknown"),
        )

    async def _log_response(
        self, request: Request, response: Response, process_time: float
    ):
        """记录响应信息"""
        if not self.logging_enabled or request.url.path in self.log_exclude_paths:
            return

        self.logger.info(
            f"请求完成: {request.method} {request.url.path} with status %d in %.4f seconds",
            response.status_code,
            process_time,
        )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        """
        中间件调度函数。
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
                f"请求异常: {request.method} {request.url.path} after %.4f seconds",
                process_time,
            )
            raise e
        finally:
            if token:
                trace_context.reset_trace_id(token)

        return response 