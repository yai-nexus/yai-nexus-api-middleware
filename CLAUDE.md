# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses Python with `pyproject.toml` configuration:

- **Install dependencies**: `pip install -e .`
- **Install with development dependencies**: `pip install -e ".[dev]"`
- **Run tests**: `pytest` (uses paths configured in pyproject.toml: `pythonpath = [".", "src"]`)
- **Run examples**: `uvicorn examples.simple_usage:app --reload --port 8000`

## Architecture Overview

This is a FastAPI middleware library (`yai_nexus_api_middleware`) that provides:

1. **Fluent Builder Pattern**: The `MiddlewareBuilder` class uses method chaining to configure middleware stack
2. **Modular Middleware Features**:
   - Tracing (with configurable headers)
   - Identity parsing (tenant, user, staff IDs from headers)
   - Request/response logging
   - Standard response wrapping (ApiResponse format)

3. **Key Components**:
   - `src/yai_nexus_api_middleware/builder.py`: Main builder class and dependency injection functions
   - `src/yai_nexus_api_middleware/models.py`: Data models (UserInfo, StaffInfo, ApiResponse)
   - `src/yai_nexus_api_middleware/decorators.py`: Response decorators like `@allow_raw_response`
   - `src/yai_nexus_api_middleware/internal/`: Internal implementation details
   - `examples/simple_usage.py`: Complete working example

4. **Response Handling**: The middleware enforces ApiResponse format for all endpoints unless marked with `@allow_raw_response`

## Project Structure

Follows standard Python packaging with:
- `src/yai_nexus_api_middleware/`: Main package code
- `src/yai_nexus_api_middleware/internal/`: Internal implementation (not part of public API)
- `examples/`: Usage examples
- `pyproject.toml`: Project configuration with dependencies and test settings

## Dependencies

Core dependencies:
- `fastapi`: Web framework
- `pydantic`: Data validation
- `yai-nexus-logger`: Logging (part of yai-nexus ecosystem)
- `yai-nexus-configuration`: Configuration management

## Code Style

- Uses Chinese comments and docstrings (per .cursor/rules/yai-open-source.mdc)
- Type hints required for function parameters and return values
- Follows PEP 8 style guidelines
- Uses f-strings for string formatting
- Single responsibility principle for functions and classes

## Testing

- Uses pytest framework
- Test files should be named `test_*.py`
- Test functions should be named `test_具体功能描述` (Chinese descriptive names)
- Tests should be independent and repeatable
- Uses fixtures like `tmp_path` and `capsys` when needed