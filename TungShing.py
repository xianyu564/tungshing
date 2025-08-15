from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from tungshing import TungShing  # 兼容旧路径：导入新包


if __name__ == "__main__":
    # 兼容性示例：
    ts = TungShing(datetime.now(ZoneInfo("Asia/Shanghai")))
    print(ts.year8Char, ts.month8Char, ts.day8Char)
