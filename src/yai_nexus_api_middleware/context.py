from contextvars import ContextVar, Token
from typing import Optional
import uuid

# 用于存储 trace_id 的上下文变量，提供一个默认值以避免在未设置时出错。
_trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


def get_trace_id() -> str:
    """
    从当前上下文中获取 trace_id。
    """
    return _trace_id_var.get()


def set_trace_id(trace_id: Optional[str] = None) -> Token:
    """
    在上下文中设置 trace_id。

    如果未提供 trace_id，将自动生成一个新的 UUID v4 作为 ID。
    此函数返回一个 Token，调用者可以用它来重置上下文。

    Args:
        trace_id: 要设置的追踪ID，如果为 None 则自动生成。

    Returns:
        一个用于重置上下文的 Token。
    """
    if not trace_id:
        trace_id = str(uuid.uuid4())
    return _trace_id_var.set(trace_id)


def reset_trace_id(token: Token):
    """
    使用 Token 重置 trace_id 上下文变量。
    """
    _trace_id_var.reset(token) 