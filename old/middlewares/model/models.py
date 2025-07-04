from pydantic import BaseModel, ConfigDict
from typing import Optional
from fastapi import Request


class UniqTenantUserInfo(BaseModel):
    """Model for tenant user information."""

    model_config = ConfigDict(populate_by_name=True)

    uniqTenantId: Optional[str] = None
    uniqUserId: Optional[str] = None


class UniqTenantStaffInfo(BaseModel):
    """Model for tenant staff information."""

    model_config = ConfigDict(populate_by_name=True)

    uniqTenantId: Optional[str] = None
    uniqStaffId: Optional[str] = None


async def get_current_user(request: Request) -> UniqTenantUserInfo:
    return request.state.tenant_user_info


async def get_current_staff(request: Request) -> UniqTenantStaffInfo:
    return request.state.tenant_staff_info
