"""
YAI Nexus API Middleware

A modern, fluent, and elegant API middleware for FastAPI, 
built for the yai-nexus ecosystem.
"""

__version__ = "0.1.0"

from .builder import MiddlewareBuilder
from .models import UserInfo, StaffInfo
from .dependencies import get_current_user, get_current_staff
from .responses import ApiResponse

# TODO: Add dependency injection functions for user/staff info

__all__ = [
    # Builder
    "MiddlewareBuilder",
    # Models
    "UserInfo",
    "StaffInfo",
    "ApiResponse",
    # Dependencies
    "get_current_user",
    "get_current_staff",
] 