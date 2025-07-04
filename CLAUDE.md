# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses Python with `pyproject.toml` configuration:

- **Install dependencies**: `pip install -e .`
- **Install with development dependencies**: `pip install -e ".[dev]"`
- **Run tests**: `pytest` (uses paths configured in pyproject.toml: `pythonpath = [".", "src"]`)
- **Run single test file**: `pytest tests/integration/test_middleware_integration.py`
- **Run examples**: `uvicorn examples.simple_usage:app --reload --port 8000`
- **Alternative example run**: `python examples/simple_usage.py` (runs on host 0.0.0.0:8000)

## Architecture Overview

This is a FastAPI middleware library (`yai_nexus_api_middleware`) that provides:

1. **Fluent Builder Pattern**: The `MiddlewareBuilder` class uses method chaining to configure middleware stack
2. **Modular Middleware Features**:
   - Tracing (with configurable headers)
   - Identity parsing (tenant, user, staff IDs from headers)
   - Request/response logging
   - Standard response wrapping (ApiResponse format)

3. **Key Components**:
   - `src/yai_nexus_api_middleware/builder.py`: Main `MiddlewareBuilder` class with fluent configuration API
   - `src/yai_nexus_api_middleware/models.py`: Data models (UserInfo, StaffInfo)
   - `src/yai_nexus_api_middleware/responses.py`: `ApiResponse` model for standardized responses
   - `src/yai_nexus_api_middleware/dependencies.py`: FastAPI dependency functions (`get_current_user`, `get_current_staff`)
   - `src/yai_nexus_api_middleware/internal/core_middleware.py`: Core ASGI middleware implementation
   - `examples/simple_usage.py`: Complete working example with trace context usage

4. **Response Handling**: All endpoints should return `ApiResponse.success()` or `ApiResponse.failure()` for consistent JSON structure

## Project Structure

Follows standard Python packaging with:
- `src/yai_nexus_api_middleware/`: Main package code
- `src/yai_nexus_api_middleware/internal/`: Internal implementation (not part of public API)
- `examples/`: Usage examples
- `pyproject.toml`: Project configuration with dependencies and test settings

## Dependencies

Core dependencies:
- `fastapi>=0.100.0`: Web framework
- `pydantic>=2.0.0`: Data validation and models
- `yai-nexus-logger==0.2.2`: Logging with trace context support (part of yai-nexus ecosystem)

## Code Style

- Uses Chinese comments and docstrings (per .cursor/rules/yai-open-source.mdc)
- Type hints required for function parameters and return values
- Follows PEP 8 style guidelines
- Uses f-strings for string formatting
- Single responsibility principle for functions and classes

## Middleware Configuration Pattern

The middleware uses a fluent builder pattern with three main configuration methods:

1. **Tracing**: `with_tracing(header="X-Request-ID")` - Enables distributed tracing
2. **Identity**: `with_identity_parsing(tenant_id_header="X-Tenant-ID", user_id_header="X-User-ID", staff_id_header="X-Staff-ID")` - Extracts user context from headers
3. **Logging**: `with_request_logging(exclude_paths=["/health"])` - Logs all requests except specified paths

Always call `.build()` to apply the middleware to the FastAPI app.

## Trace Context Integration

- Use `trace_context.get_trace_id()` from `yai-nexus-logger` to access current trace ID in business logic
- Trace IDs are automatically included in `ApiResponse` objects and injected into all log records
- Configure logging with both console and file handlers for development: `LoggerConfigurator().with_console_handler().with_file_handler(path="logs/filename.log")`

## Testing

The project has comprehensive test coverage with 51+ tests across multiple categories:

### Test Structure
- **Unit Tests** (`tests/unit/`): Test individual components in isolation
  - `test_models.py`: UserInfo and StaffInfo model validation (10 tests)
  - `test_responses.py`: ApiResponse creation and validation (8 tests)  
  - `test_dependencies.py`: Dependency injection functions (9 tests)
  - `test_builder.py`: MiddlewareBuilder configuration (12 tests)

- **Integration Tests** (`tests/integration/`): Test complete middleware functionality
  - `test_simple_middleware_integration.py`: End-to-end middleware testing (12+ tests)

### Test Guidelines
- Uses pytest framework with `pytest` command
- Test files should be named `test_*.py`
- Test functions should be named `test_具体功能描述` (Chinese descriptive names)
- Tests should be independent and repeatable
- Run all tests: `pytest tests/unit/ tests/integration/test_simple_middleware_integration.py`
- Test dependencies include: `pytest>=7.0.0`, `httpx>=0.24.0`, `uvicorn[standard]>=0.20.0`

### What Tests Cover
- Model creation, validation, and serialization
- ApiResponse success/failure scenarios with automatic trace_id injection
- Dependency injection for user/staff context extraction
- Builder pattern configuration and middleware application
- Complete request/response flows with tracing, identity parsing, and logging
- Concurrent request handling and trace_id consistency
- Error handling and edge cases
