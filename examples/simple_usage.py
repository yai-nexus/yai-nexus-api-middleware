import uvicorn
from fastapi import FastAPI, Depends
from typing import Optional

# 在一个实际的项目中, 你可能需要这样导入, 取决于 __init__.py 的配置:
# from yai_nexus_api_middleware import MiddlewareBuilder, get_current_user, UserInfo
from yai_nexus_api_middleware.builder import MiddlewareBuilder
from yai_nexus_api_middleware.dependencies import get_current_user
from yai_nexus_api_middleware.models import UserInfo

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
        .build()
)


# 3. 创建 API 端点
@app.get("/")
async def read_root(user: Optional[UserInfo] = Depends(get_current_user)):
    """
    一个示例端点，演示如何使用依赖注入来获取用户信息。
    """
    if user and user.user_id:
        return {"message": f"你好, 来自租户 {user.tenant_id} 的用户 {user.user_id}!"}
    return {"message": "你好, 匿名用户!"}


@app.get("/health")
async def health_check():
    """
    一个健康检查端点，这个端点的日志将被忽略。
    """
    return {"status": "ok"}


# --- 如何运行这个示例 ---
#
# 1. 确保你已经安装了所有依赖 (在项目根目录运行):
#    pip install -e .
#    pip install "uvicorn[standard]"
#
# 2. 在你的终端中，使用以下命令启动服务器:
#    uvicorn examples.simple_usage:app --reload --port 8000
#
# 3. 使用 curl 或浏览器来测试:
#
#    - 基本请求 (匿名):
#      curl http://127.0.0.1:8000/
#
#    - 模拟带有身份信息的请求:
#      curl -H "X-Tenant-ID: t-Bess" -H "X-User-ID: u-King" -H "X-Request-ID: trace-me-123" http://127.0.0.1:8000/
#
#    - 访问被日志排除的路径:
#      curl http://127.0.0.1:8000/health
#
#    观察终端中由 yai-nexus-logger 输出的 JSON 格式日志。
if __name__ == "__main__":
    uvicorn.run("examples.simple_usage:app", host="0.0.0.0", port=8000, reload=True) 