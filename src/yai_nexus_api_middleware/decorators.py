"""
提供一个装饰器，用于从 YAI Nexus API 中间件的标准化响应处理中排除特定端点。
"""

from functools import wraps


def allow_raw_response(func):
    """
    一个装饰器，用于标记某个端点允许返回原始响应，
    而不是强制使用 ApiResponse 进行包装。

    当一个端点被这个装饰器标记后, StandardResponseMiddleware 将会忽略它,
    允许它直接返回任何兼容 JSON 的数据结构。

    示例:
        from fastapi import FastAPI
        from yai_nexus_api_middleware.decorators import allow_raw_response

        app = FastAPI()

        @app.get("/raw-data")
        @allow_raw_response
        def get_raw_data():
            return {"message": "这是一个原始响应"}
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 装饰器实际上不需要执行任何操作，它只是一个标记。
        # 使用 @wraps 来保留原始函数的元数据。
        # 实际的逻辑将在中间件中处理。
        return func(*args, **kwargs)

    # 给函数附加一个标记，供中间件检查
    setattr(wrapper, '_allow_raw_response', True)
    return wrapper 