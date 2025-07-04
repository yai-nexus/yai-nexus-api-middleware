# 方案 1B: 实现计划 (Composition over Consolidation)

我们已经确定采用方案 1B 来重构中间件。此方案的核心思想是，`CoreMiddleware` 作为主入口，将标准响应的处理逻辑**委托**给一个独立的、非中间件的 `StandardResponseHandler` 类。

以下是详细的、分步的实现计划。

---

### 第一步: 创建 `StandardResponseHandler`

这个类是本次重构的核心。它将包含所有之前在 `StandardResponseMiddleware` 中的逻辑，但它本身不是一个中间件。

1.  **文件路径**: `src/yai_nexus_api_middleware/internal/standard_response_handler.py` (创建一个新文件)。
2.  **类定义**:
    ```python
    # src/yai_nexus_api_middleware/internal/standard_response_handler.py
    import json
    from fastapi import Request, Response
    from starlette.responses import JSONResponse
    from yai_nexus_logger import get_logger
    from ..responses import ApiResponse

    class StandardResponseHandler:
        def __init__(self):
            self.logger = get_logger(__name__)

        def process(self, request: Request, response: Response) -> Response:
            # 这里将包含原来 StandardResponseMiddleware.dispatch 的所有逻辑
            # ...
    ```
3.  **逻辑迁移**: 将 `StandardResponseMiddleware` 的 `dispatch` 方法中的全部代码（豁免检查、JSON检查、格式校验、错误包装、trace_id 注入等）完整地复制到 `StandardResponseHandler.process` 方法中。
    *   **注意**: 其中的 `trace_id` 获取逻辑，即 `getattr(request.state, "trace_id", None)`，将保持不变，因为我们预期 `CoreMiddleware` 会把它放到 `request.state` 中。

---

### 第二步: 修改 `CoreMiddleware` 以使用 `StandardResponseHandler`

`CoreMiddleware` 将转变为一个协调者，在启用标准响应功能时，它会实例化并调用 `StandardResponseHandler`。

1.  **文件路径**: `src/yai_nexus_api_middleware/internal/core_handlers.py`。
2.  **导入**: 在文件顶部添加 `from .standard_response_handler import StandardResponseHandler`。
3.  **`__init__` 方法修改**:
    *   接收 `standard_response_enabled: bool` 参数。
    *   在 `__init__` 中增加一个新成员 `self.response_handler = None`。
    *   如果 `standard_response_enabled` 为 `True`，则实例化 `self.response_handler = StandardResponseHandler()`。
4.  **`dispatch` 方法修改**:
    *   在 `response = await call_next(request)` 之后。
    *   添加一个判断：`if self.response_handler:`。
    *   在判断内部，调用 `response = self.response_handler.process(request, response)`。

---

### 第三步: 更新 `MiddlewareBuilder`

建造者需要更新，以正确配置 `CoreMiddleware`，并移除对旧中间件的引用。

1.  **文件路径**: `src/yai_nexus_api_middleware/builder.py`。
2.  **移除导入**: 删除 `from .internal.standard_response import StandardResponseMiddleware`。
3.  **`build` 方法修改**:
    *   确保只添加 `CoreMiddleware`。
    *   将 `self._standard_response_enabled` 标志位作为 `standard_response_enabled` 参数传递给 `CoreMiddleware` 的构造函数。

---

### 第四步: 清理工作

完成上述步骤后，旧的 `StandardResponseMiddleware` 文件就不再需要了。

1.  **删除文件**: 删除 `src/yai_nexus_api_middleware/internal/standard_response.py`。

---

### 最终验证

完成所有编码后，我们将执行与之前相同的测试流程：

1.  启动 `examples/simple_usage.py`。
2.  使用 `curl` 调用 `/report` 端点，并传入 `X-Request-ID` 请求头。
3.  断言返回的 JSON 响应体中，顶层的 `trace_id` 字段被正确地填充了值。

这个计划涵盖了从编码到清理的完整流程，每一步都清晰明确，风险可控。请您审阅此计划。 