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


class Page(BaseModel, Generic[T]):
    """
    用于分页数据的 Pydantic 模型。
    """
    items: List[T] = Field(..., description="当前页的数据项")
    page_index: int = Field(1, ge=1, description="当前页码")
    page_size: int = Field(10, ge=1, description="每页大小")
    total_items: int = Field(0, description="总项目数")
    total_pages: Optional[int] = Field(0, description="总页数")

    @field_validator("total_pages", always=True)
    def compute_total_pages(cls, v, values):
        """
        自动计算总页数。
        """
        data = values.data
        total_items = data.get("total_items")
        page_size = data.get("page_size")
        if total_items is not None and page_size is not None and page_size > 0:
            # 向上取整除法
            return (total_items + page_size - 1) // page_size
        return 0 