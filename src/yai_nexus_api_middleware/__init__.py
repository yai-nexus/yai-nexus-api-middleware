"""
YAI Nexus API Middleware

A modern, fluent, and elegant API middleware for FastAPI, 
built for the yai-nexus ecosystem.
"""

__version__ = "0.1.0"

from .builder import MiddlewareBuilder
from .models import UserInfo, StaffInfo, GatewayResponse

# TODO: Add dependency injection functions for user/staff info

__all__ = [
    "MiddlewareBuilder",
    "UserInfo",
    "StaffInfo",
    "GatewayResponse"
] 