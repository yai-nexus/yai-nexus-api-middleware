from pydantic import BaseModel, Field, field_validator
from typing import Generic, TypeVar, List, Optional

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


class GatewayResponse(BaseModel, Generic[T]):
    """
    标准化的 API 响应包装器。
    """
    data: Optional[T] = Field(None, description="业务数据")
    code: str = Field("0", description="状态码，'0' 代表成功")
    message: str = Field("操作成功", description="人类可读的操作消息")
    trace_id: Optional[str] = Field(None, description="用于链路追踪的请求ID")
