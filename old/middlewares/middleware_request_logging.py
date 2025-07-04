#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: Nero Claudius
@date: 2025/3/3
@version: 0.0.1
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from lucas_common_components.logging.logger import setup_logger

logger = setup_logger(__name__)


async def format_curl(request: Request) -> str:
    """将请求格式化为 curl 命令格式"""
    headers = " ".join([f"-H '{k}: {v}'" for k, v in request.headers.items()])

    # 获取请求体
    body = ""
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body_bytes = await request.body()
            body = body_bytes.decode("utf-8")
            if body:
                body = f"-d '{body}'"
        except Exception:
            pass

    return f"curl -X {request.method} {headers} {body} {request.url}"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始
        start_time = time.time()

        # 记录请求信息
        curl_command = await format_curl(request)
        logger.info(
            f"Started {request.method} {request.url.path} "
            f"[REQUEST_ID:{request_id}] "
            f"Client:{request.client.host}:{request.client.port} "
            f"User-Agent:{request.headers.get('user-agent', 'Unknown')}\n"
            f"CURL: {curl_command}"
        )

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录响应信息
            logger.info(
                f"Completed {request.method} {request.url.path} "
                f"[REQUEST_ID:{request_id}] "
                f"Status:{response.status_code} "
                f"Time:{process_time:.3f}s"
            )

            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            # 记录异常信息
            process_time = time.time() - start_time
            logger.error(
                f"Failed {request.method} {request.url.path} "
                f"[REQUEST_ID:{request_id}] "
                f"Error:{str(e)} "
                f"Time:{process_time:.3f}s"
            )
            raise
