# YAI Nexus API Middleware

[![PyPI version](https://badge.fury.io/py/yai-nexus-api-middleware.svg)](https://badge.fury.io/py/yai-nexus-api-middleware)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)

一个为 FastAPI 设计的、功能强大且易于使用的中间件，旨在统一 Y-AI Nexus 生态系统中的 API 行为。它通过提供请求追踪、身份解析、结构化日志和标准化的响应格式，极大地简化了 API 的开发和维护。

## ✨ 功能特性

- **流式配置 API**: 使用优雅的建造者模式（Builder Pattern）进行中间件的配置，代码清晰易读。
- **分布式追踪**: 自动处理请求头中的 `X-Request-ID` (可配置)，并将其注入日志上下文和 API 响应中，轻松实现跨服务追踪。
- **用户身份解析**: 从请求头中提取租户和用户信息，并通过 FastAPI 的依赖注入系统在端点中轻松获取。
- **自动化请求日志**: 自动记录所有传入请求的详细信息，包括路径、方法、IP 和处理时间，并允许轻松排除健康检查等特定端点。
- **标准化响应模型**: 提供 `ApiResponse` 模型，强制 API 返回统一的 JSON 结构 (`{code, message, data, trace_id}`)，提升前端协作效率和系统的健壮性。
- **与 `yai-nexus-logger` 深度集成**: 无缝集成 `yai-nexus-logger`，将追踪 ID 和其他上下文信息自动添加到每一条日志记录中。

## 🚀 安装

通过 pip 安装：
```bash
pip install yai-nexus-api-middleware
```

## 💡 快速开始

以下是一个如何在 FastAPI 应用中配置和使用此中间件的简单示例。

### 1. 准备 FastAPI 应用和日志

首先，确保你已经安装了 `fastapi`, `uvicorn` 和 `yai-nexus-logger`。

```python
# main.py
import uvicorn
from fastapi import FastAPI, Depends
from typing import Optional

# 导入中间件和相关组件
from yai_nexus_api_middleware import MiddlewareBuilder, get_current_user, UserInfo, ApiResponse
from yai_nexus_logger import LoggerConfigurator, init_logging, get_logger

# 初始化日志系统
init_logging(LoggerConfigurator().with_console_handler())
logger = get_logger(__name__)

# 创建 FastAPI 应用实例
app = FastAPI(title="YAI Nexus API Middleware 示例")
```

### 2. 配置并应用中间件

使用 `MiddlewareBuilder` 的流式 API 来添加所需功能。

```python
# main.py (续)

(
    MiddlewareBuilder(app)
        .with_tracing(header="X-Request-ID")
        .with_identity_parsing(
            tenant_id_header="X-Tenant-ID",
            user_id_header="X-User-ID",
        )
        .with_request_logging(exclude_paths=["/health"])
        .build()
)
```

**配置说明**:
- `.with_tracing()`: 启用分布式追踪，从 `X-Request-ID` 头获取 trace_id。
- `.with_identity_parsing()`: 启用身份解析，从 `X-Tenant-ID` 和 `X-User-ID` 头获取用户信息。
- `.with_request_logging()`: 启用请求日志，但忽略对 `/health` 路径的记录。
- `.build()`: 完成配置并应用中间件。

### 3. 创建合规的 API 端点

在你的端点中，使用 `ApiResponse` 来构造返回结果，并使用 `Depends(get_current_user)` 来获取当前用户信息。

```python
# main.py (续)

@app.get("/", response_model=ApiResponse)
async def read_root(user: Optional[UserInfo] = Depends(get_current_user)):
    """
    一个合规的示例端点。
    """
    if user and user.user_id:
        message = f"你好, 来自租户 {user.tenant_id} 的用户 {user.user_id}!"
    else:
        message = "你好, 匿名用户!"
    
    logger.info(f"Trace ID 已自动注入此日志")
    
    return ApiResponse.success(data={"message": message})

@app.get("/items/{item_id}", response_model=ApiResponse)
async def get_item(item_id: str):
    """
    演示失败响应的端点。
    """
    if item_id == "foo":
        return ApiResponse.success(data={"item_id": item_id, "name": "一个有效的物品"})
    else:
        return ApiResponse.failure(
            code="ITEM_NOT_FOUND",
            message=f"ID 为 '{item_id}' 的物品不存在。"
        )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

### 4. 运行和测试

将以上代码保存为 `main.py`，然后使用 uvicorn 运行：

```bash
uvicorn main:app --reload
```

现在，你可以通过 `curl` 或浏览器进行测试：

**测试匿名访问**:
```bash
curl http://127.0.0.1:8000/
```
```json
{
  "code": "0",
  "message": "操作成功",
  "data": {
    "message": "你好, 匿名用户!"
  },
  "trace_id": "a-random-uuid-string"
}
```

**测试身份和追踪**:
```bash
curl -H "X-Request-ID: my-trace-id-123" \
     -H "X-Tenant-ID: tenant-001" \
     -H "X-User-ID: user-abc" \
     http://127.0.0.1:8000/
```
```json
{
  "code": "0",
  "message": "操作成功",
  "data": {
    "message": "你好, 来自租户 tenant-001 的用户 user-abc!"
  },
  "trace_id": "my-trace-id-123"
}
```
同时，你的控制台日志中将自动包含 `my-trace-id-123`。

**测试失败响应**:
```bash
curl http://127.0.0.1:8000/items/bar
```
```json
{
  "code": "ITEM_NOT_FOUND",
  "message": "ID 为 'bar' 的物品不存在。",
  "data": null,
  "trace_id": "another-random-uuid"
}
```

## 🤝 贡献

欢迎提交问题和拉取请求。对于重大更改，请先开启一个问题讨论您想要更改的内容。

## 📜 许可证

本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证。
