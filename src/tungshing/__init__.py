from .core import TungShing

try:  # 从安装的元数据中导出版本号 / Expose version from package metadata
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("tungshing")
except Exception:  # 运行源码树时可能无法解析
    __version__ = "0.0.0"

__all__ = ["TungShing", "__version__"]


