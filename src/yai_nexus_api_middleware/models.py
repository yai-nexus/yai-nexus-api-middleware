from pydantic import BaseModel
from typing import TypeVar, Optional

T = TypeVar("T")


class UserInfo(BaseModel):
    """
    模型，用于存储从请求头解析出的租户用户信息。
    """
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None


class StaffInfo(BaseModel):
    """
    模型，用于存储从请求头解析出的租户员工信息。
    """
    tenant_id: Optional[str] = None
    staff_id: Optional[str] = None

