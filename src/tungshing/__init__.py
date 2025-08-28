"""
TungShing - 严格口径的黄历/通胜

A highly accurate Chinese lunar calendar library with strict standards compliance.
Provides precise timing calculations following GB/T 33661-2017 national standards.

Features:
- Year pillar switches at Lichun (Beginning of Spring) with second precision
- Month pillar switches only at "Jie" solar terms (not "Zhongqi")  
- Day pillar starts next day from 23:00
- Full API compatibility with cnlunar
- Professional timezone handling

Example usage:
    >>> from tungshing import TungShing
    >>> from datetime import datetime
    >>> ts = TungShing(datetime(2025, 2, 3, 22, 30))
    >>> ts.year8Char  # Year pillar in Ganzhi notation
    '甲辰'
    >>> ts.lunarDayCn  # Lunar day in Chinese
    '初五'

For more information, see: https://github.com/xianyu564/tungshing
"""

from .core import TungShing

try:  # 从安装的元数据中导出版本号 / Expose version from package metadata
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("tungshing")
except Exception:  # 运行源码树时可能无法解析 / Fallback for source tree
    from ._version import __version__

__all__ = ["TungShing", "__version__"]

# Package metadata for introspection
__author__ = "Zhang Xianyu (张衔瑜) / Zhang Ziyang (张子阳)"
__email__ = "z_zz@u.nus.edu"
__license__ = "MIT"
__description__ = "严格口径的黄历/通胜（年柱立春、月柱按节、日柱晚子时）；兼容 cnlunar 用法"


