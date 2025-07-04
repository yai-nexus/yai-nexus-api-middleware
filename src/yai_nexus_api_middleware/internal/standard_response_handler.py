import json
from fastapi import Request, Response
from starlette.responses import JSONResponse
from yai_nexus_logger import get_logger, trace_context

from yai_nexus_api_middleware.responses import ApiResponse


class StandardResponseHandler:
    """
    标准响应处理器，用于强制端点的返回结果是标准的 ApiResponse 格式。
    """

    def __init__(self):
        self.logger = get_logger(__name__)

    def process(self, request: Request, response: Response) -> Response:
        """
        处理响应，确保符合 ApiResponse 格式。
        """
        # 1. 检查端点是否使用 @allow_raw_response 装饰器进行了豁免
        endpoint = request.scope.get("endpoint")
        if not endpoint or hasattr(endpoint, "_allow_raw_response"):
            return response

        # 2. 只处理成功的(2xx) JSON 响应
        is_json_response = isinstance(response, JSONResponse)
        is_success_status = 200 <= response.status_code < 300
        if not (is_json_response and is_success_status):
            return response

        # 3. 解析响应体
        try:
            data = json.loads(response.body)
        except (json.JSONDecodeError, TypeError):
            # 对于一个有效的 JSONResponse 来说，这不应该发生，但作为安全措施
            return response

        # 4. 校验响应是否已经符合 ApiResponse 的结构
        if isinstance(data, dict) and "code" in data and "message" in data:
            # 格式正确，仅当缺少 trace_id 时补充
            if "trace_id" not in data or not data["trace_id"]:
                trace_id = getattr(request.state, "trace_id", None) or trace_context.get_trace_id()
                if trace_id:
                    data["trace_id"] = trace_id
                    return JSONResponse(
                        content=data,
                        status_code=response.status_code,
                        headers=response.headers,
                    )
            return response
        else:
            # 5. 校验失败：返回一个标准的 500 错误
            endpoint_name = getattr(endpoint, "__name__", request.url.path)
            error_message = (
                f"开发错误: 端点 '{endpoint_name}' 未能返回一个标准的 ApiResponse 对象。"
            )
            self.logger.error(
                "检测到不合规的 API 响应. Endpoint: %s, Response Body Preview: %s",
                endpoint_name,
                response.body.decode(errors="ignore")[:200],
            )

            error_response = ApiResponse.failure(
                code="ERR_INVALID_RESPONSE_FORMAT", message=error_message
            )
            error_response.trace_id = getattr(request.state, "trace_id", None) or trace_context.get_trace_id()

            return JSONResponse(
                content=error_response.model_dump(by_alias=True),
                status_code=500,  # Internal Server Error
            )