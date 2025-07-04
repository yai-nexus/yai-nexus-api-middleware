from lucas_common_components.middlewares.middleware_identity_parser import (
    IdentityParserMiddleware,
)
from lucas_common_components.middlewares.middleware_request_logging import (
    RequestLoggingMiddleware,
)
from lucas_common_components.middlewares.middleware_trace_parser import TraceParser


def setup_middleware(app):
    # 身份解析中间件必须最先执行
    app.add_middleware(IdentityParserMiddleware)

    app.add_middleware(TraceParser)
    # 其他中间件
    app.add_middleware(RequestLoggingMiddleware)
