"""
此模块提供用于创建标准 ApiResponse 对象的辅助函数。
"""
from typing import Any, Optional, TypeVar
from pydantic import BaseModel, Field
from typing import Generic


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    标准化的 API 响应包装器。
    """
    code: str = Field("0", description="状态码，'0' 代表成功")
    message: str = Field("操作成功", description="人类可读的操作消息")
    data: Optional[T] = Field(None, description="业务数据")
    trace_id: Optional[str] = Field(None, description="用于链路追踪的请求ID")

    @staticmethod
    def success(data: Optional[Any] = None) -> "ApiResponse[T]":
        """
        创建一个表示成功的 ApiResponse。

        Args:
            data: 要包含在响应中的业务数据。

        Returns:
            一个配置为成功状态的 ApiResponse 对象。
        """
        return ApiResponse(data=data)

    @staticmethod
    def failure(code: str, message: str, data: Optional[Any] = None) -> "ApiResponse[T]":
        """
        创建一个表示错误的 ApiResponse。

        Args:
            code: 错误代码。
            message: 人类可读的错误消息。
            data: 可选的，与错误相关的额外数据。

        Returns:
            一个配置为错误状态的 ApiResponse 对象。
        """
        if code == "0":
            raise ValueError("错误响应的代码不能为 '0'")
        return ApiResponse(code=code, message=message, data=data) 