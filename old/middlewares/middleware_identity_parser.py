#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: Nero Claudius
@date: 2025/3/3
@version: 0.0.1
"""

from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from lucas_common_components.middlewares.model.models import (
    UniqTenantUserInfo,
    UniqTenantStaffInfo,
)
from lucas_common_components.logging.logger import setup_logger

logger = setup_logger(__name__)


async def get_header_value(request: Request, header_name: str) -> Optional[str]:
    """Get header value from request with consistent naming convention."""
    return request.headers.get(f"Lucas-uniq-{header_name}")


class IdentityParserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Parse user identity information
        request.state.tenant_user_info = UniqTenantUserInfo(
            uniqTenantId=await get_header_value(request, "TenantId"),
            uniqUserId=await get_header_value(request, "UserId"),
        )

        # Parse staff identity information
        request.state.tenant_staff_info = UniqTenantStaffInfo(
            uniqTenantId=await get_header_value(request, "TenantId"),
            uniqStaffId=await get_header_value(request, "StaffId"),
        )

        return await call_next(request)
