import importlib
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI

from lucas_common_components.logging import setup_logger

logger = setup_logger(__name__)


def setup_routers(
    app: FastAPI,
    project_root: str = "src",
    prefix: str = "",
    recursive: bool = True,
    exclude_dirs: Optional[List[str]] = None,
) -> None:
    """
    自动注册所有路由模块

    Args:
        app: FastAPI应用实例
        project_root: 项目根目录路径，默认为"src"
        prefix: 路由前缀，默认为空字符串
        dependencies: 自定义依赖项列表，如果为None则使用默认的认证依赖
        recursive: 是否递归扫描子目录，默认为True
        exclude_dirs: 要排除的目录列表，默认为None
    """
    # 设置默认依赖项

    # 设置默认排除目录
    if exclude_dirs is None:
        exclude_dirs = [
            "__pycache__",
            "tests",
            "migrations",
            "venv",
            ".git",
            ".idea",
            ".vscode",
        ]

    # 获取项目根目录的路径
    root_dir = Path(project_root).resolve()

    # 确保目录存在
    if not root_dir.exists():
        logger.error(f"目录不存在: {root_dir}")
        return

    def get_module_path(file_path: Path) -> str:
        """将文件路径转换为模块路径"""
        try:
            # 获取相对于项目根目录的路径
            relative_path = file_path.relative_to(root_dir)
            # 转换为模块路径格式
            module_path = str(relative_path).replace("/", ".").replace("\\", ".")
            return module_path
        except ValueError:
            logger.error(f"无法获取相对路径: {file_path}")
            return ""

    def scan_directory(directory: Path) -> None:
        """递归扫描目录中的Python模块"""
        try:
            for item in directory.iterdir():
                # 跳过排除的目录
                if item.name in exclude_dirs:
                    continue

                if (
                    item.is_file()
                    and item.name.endswith(".py")
                    and not item.name.startswith("__")
                ):
                    try:
                        # 构建完整的模块路径
                        module_path = get_module_path(item)
                        if not module_path:
                            continue

                        module_name = module_path[:-3]  # 移除.py后缀

                        # 动态导入模块
                        module = importlib.import_module(module_name)

                        # 查找并注册router对象
                        if hasattr(module, "router"):
                            # 如果模块中定义了router_prefix，使用模块中的前缀
                            router_prefix = getattr(module, "router_prefix", prefix)

                            app.include_router(module.router, prefix=router_prefix)
                            logger.info(f"成功注册路由模块: {module_name}")
                        else:
                            logger.debug(
                                f"模块 {module_name} 中未找到router对象，已跳过"
                            )

                    except ModuleNotFoundError as e:
                        logger.error(f"导入路由模块 {module_name} 失败: {str(e)}")
                    except Exception as e:
                        logger.error(
                            f"注册路由模块 {module_name} 时出错: {str(e)}",
                            exc_info=True,
                        )

                elif item.is_dir() and recursive and not item.name.startswith("__"):
                    # 递归扫描子目录
                    scan_directory(item)
        except Exception as e:
            logger.error(f"扫描目录 {directory} 时出错: {str(e)}", exc_info=True)

    try:
        # 开始扫描目录
        scan_directory(root_dir)
        logger.info(f"路由注册完成，项目根目录: {root_dir}")
    except Exception as e:
        logger.error(f"扫描路由目录时出错: {str(e)}", exc_info=True)
