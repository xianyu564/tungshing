### 贡献指南 · Contributing

本文档以中文为准，同时提供英文要点（Chinese is authoritative; English notes included）。

感谢你愿意为 TungShing 贡献！以下是基本流程（Below is the basic workflow）：

1. Fork 本仓库，创建特性分支：`feat/your-feature` 或修复分支：`fix/your-bug`。
2. 安装依赖并运行测试：
   - `pip install -e .[dev]`
   - `pytest -q`
3. 确保修改不破坏“严格口径”定义（Ensure the strict rules stay intact）：
   - 年柱以“立春”为界（精确到分秒）
   - 月柱以“节”交节为界（不是中气）
   - 日柱 23:00 起算次日；23:00–23:59 期间对象整体按“次日口径”转发
   - 规范依据：GB/T 33661-2017《农历的编算和颁行》（Standards: GB/T 33661-2017）
4. 提交 PR（Submit PR）：
   - 清晰描述改动动机、口径影响与测试覆盖
   - 如引入新依赖，请在 `pyproject.toml` 中注明，并解释必要性

问题反馈请使用 Issues 模板，尽量提供：Python 版本、操作系统、最小复现代码和期望/实际结果。
For issues, please include Python version, OS, minimal reproduction, expected vs. actual.


