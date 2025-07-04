#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: Nero Claudius
@date: 2025/3/3
@version: 0.0.1
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from lucas_common_components.trace import trace_context
from lucas_common_components.logging.logger import setup_logger

logger = setup_logger(__name__)


class TraceParser(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        trace_id = request.headers.get("lucas-trace-id")
        logger.debug(f"trace parser get trace_id: {trace_id}")
        token = None
        if trace_id:
            # 设置 trace_id，并获取 Token 用于请求完成后重置
            token = trace_context.set_trace_id(trace_id)

        try:
            # 继续处理请求
            response = await call_next(request)
        finally:
            # 请求完成后重置 ContextVar，相当于销毁 trace_id
            if token:
                trace_context.reset_trace_id(token)

        return response
