import uvicorn
from fastapi import FastAPI, Depends
from typing import Optional, Dict, Any

# 在一个实际的项目中, 你可以这样统一导入
from yai_nexus_api_middleware import (
    MiddlewareBuilder,
    get_current_user,
    UserInfo,
    ApiResponse,
    allow_raw_response
)

# 1. 创建 FastAPI 应用实例
app = FastAPI(title="YAI Nexus API Middleware 示例")


# 2. 使用流式建造者来配置和应用中间件
(
    MiddlewareBuilder(app)
        .with_tracing(header="X-Request-ID")
        .with_identity_parsing(
            tenant_id_header="X-Tenant-ID",
            user_id_header="X-User-ID",
            staff_id_header="X-Staff-ID",
        )
        .with_request_logging(
            exclude_paths=["/health", "/docs", "/openapi.json"]
        )
        .with_standard_response()
        .build()
)


# 3. 创建 API 端点

@app.get("/", response_model=ApiResponse)
async def read_root(user: Optional[UserInfo] = Depends(get_current_user)) -> ApiResponse:
    """
    一个合规的示例端点。
    它显式地构造并返回一个 ApiResponse 对象。
    """
    if user and user.user_id:
        message = f"你好, 来自租户 {user.tenant_id} 的用户 {user.user_id}!"
    else:
        message = "你好, 匿名用户!"
    return ApiResponse(data={"message": message})


@app.get("/bad-endpoint")
async def bad_endpoint() -> Dict[str, Any]:
    """
    一个不合规的端点。
    它返回一个原始字典，将被中间件拦截并返回 500 错误。
    """
    return {"error": "this response is not compliant"}


@app.get("/health")
@allow_raw_response
async def health_check() -> Dict[str, str]:
    """
    一个被豁免的健康检查端点。
    由于 @allow_raw_response, 它可以直接返回原始 JSON。
    """
    return {"status": "ok"}


# --- 如何运行这个示例 ---
#
# 1. 确保你已经安装了所有依赖 (在项目根目录运行):
#    pip install -e . "uvicorn[standard]"
#
# 2. 在你的终端中，使用以下命令启动服务器:
#    uvicorn examples.simple_usage:app --reload --port 8000
#
# 3. 使用 curl 或浏览器来测试:
#
#    - 调用合规的根路径:
#      curl http://127.0.0.1:8000/
#      # 预期输出: 一个标准的 ApiResponse JSON
#      # {"data":{"message":"你好, 匿名用户!"},"code":"0","message":"操作成功","trace_id":...}
#
#    - 调用不合规的路径 (注意 -i 以显示 HTTP 状态码):
#      curl -i http://127.0.0.1:8000/bad-endpoint
#      # 预期输出: HTTP/1.1 500 Internal Server Error
#      # Body: {"data":null,"code":"ERR_INVALID_RESPONSE_FORMAT","message":"开发错误: 端点 'bad_endpoint' 未能返回一个标准的 ApiResponse 对象。",...}
#
#    - 调用被豁免的路径:
#      curl http://127.0.0.1:8000/health
#      # 预期输出: {"status":"ok"}
#
#    观察终端中由 yai-nexus-logger 输出的日志。
if __name__ == "__main__":
    uvicorn.run("examples.simple_usage:app", host="0.0.0.0", port=8000, reload=True) 