"""
提供一个装饰器，用于从 YAI Nexus API 中间件的标准化响应处理中排除特定端点。
"""

import inspect
from functools import wraps
from typing import Callable, Any


def allow_raw_response(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    一个装饰器，用于标记某个端点允许返回原始响应，
    而不是强制使用 ApiResponse 进行包装。

    当一个端点被这个装饰器标记后, StandardResponseMiddleware 将会忽略它,
    允许它直接返回任何兼容 JSON 的数据结构。

    该装饰器能够正确处理同步和异步函数。

    参数:
        func: 被装饰的端点函数（同步或异步）

    返回:
        装饰后的函数，保持原有的同步/异步特性

    示例:
        from fastapi import FastAPI
        from yai_nexus_api_middleware.decorators import allow_raw_response

        app = FastAPI()

        @app.get("/raw-data")
        @allow_raw_response
        def get_raw_data():
            return {"message": "这是一个原始响应"}

        @app.get("/async-raw-data")
        @allow_raw_response
        async def get_async_raw_data():
            return {"message": "这是一个异步的原始响应"}
    """
    # 检查被装饰的函数是否是异步的
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """异步函数的包装器"""
            return await func(*args, **kwargs)
        
        # 给异步包装器附加标记，供中间件检查
        setattr(async_wrapper, '_allow_raw_response', True)
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """同步函数的包装器"""
            return func(*args, **kwargs)

        # 给同步包装器附加标记，供中间件检查
        setattr(sync_wrapper, '_allow_raw_response', True)
        return sync_wrapper 