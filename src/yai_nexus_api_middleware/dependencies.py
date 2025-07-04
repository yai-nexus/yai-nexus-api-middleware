from fastapi import Request
from typing import Optional

from .models import UserInfo, StaffInfo


def get_current_user(request: Request) -> Optional[UserInfo]:
    """
    一个 FastAPI 依赖项，用于从请求状态中获取当前用户信息。

    如果中间件未启用或未解析到用户信息，则返回 None。

    用法:
        @app.get("/")
        async def read_root(user: UserInfo = Depends(get_current_user)):
            if user and user.user_id:
                return {"message": f"Hello, user {user.user_id}!"}
            return {"message": "Hello, anonymous user!"}
    """
    return getattr(request.state, "user_info", None)


def get_current_staff(request: Request) -> Optional[StaffInfo]:
    """
    一个 FastAPI 依赖项，用于从请求状态中获取当前员工信息。

    如果中间件未启用或未解析到员工信息，则返回 None。

    用法:
        @app.get("/staff")
        async def read_staff(staff: StaffInfo = Depends(get_current_staff)):
            if staff and staff.staff_id:
                return {"message": f"Hello, staff {staff.staff_id}!"}
            return {"message": "Hello, anonymous staff!"}
    """
    return getattr(request.state, "staff_info", None) 