### TungShing · 严格口径的黄历/通胜（兼容 cnlunar 用法)

[![CI](https://github.com/xianyu564/tungshing/actions/workflows/ci.yml/badge.svg)](https://github.com/xianyu564/tungshing/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tungshing.svg)](https://pypi.org/project/tungshing/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)](#)

TungShing（通胜）是“黄历”的别名；黄历属于中国传统的“阴阳合历（Lunisolar Calendar）”。本文档以中文为准，同时提供必要的英文说明（Chinese is authoritative; English notes are provided for convenience）。

TungShing (aka Tung Shing/通胜) is an alias of the Chinese Huangli (traditional lunisolar almanac). Chinese text in this README is authoritative; English summaries are included for international users.

—

### 目录 · Table of Contents
- [国家标准依据 · National Standard](#国家标准依据--national-standard)
- [核心算法口径 · Core Algorithm Rules](#核心算法口径--core-algorithm-rules)
- [作者与动机 · Author & Motivation](#作者与动机--author--motivation)
- [术语与口径 · Terminology & Conventions](#术语与口径--terminology--conventions)
- [验证与可复现 · Validation & Reproducibility](#验证与可复现--validation--reproducibility)
- [文件结构 · Repository Structure](#文件结构--repository-structure)
- [安装 · Installation](#安装--installation)
- [快速上手 · Quick Start](#快速上手--quick-start)
- [API 说明 · API](#api-说明--api)
- [与 cnlunar / sxtwl 的差异与动机](#与-cnlunar--sxtwl-的差异与动机)
- [开发与测试 · Dev & Test](#开发与测试--dev--test)
- [变更日志 · Changelog](#变更日志--changelog)
- [致谢与引用 · Acknowledgements & References](#致谢与引用--acknowledgements--references)
- [贡献与反馈 · Contributing](#贡献与反馈--contributing)
- [许可证 · License](#许可证--license)

—

### 国家标准依据 · National Standard

- 严格遵循：GB/T 33661-2017《农历的编算和颁行》（国家质量监督检验检疫总局、国家标准化管理委员会）
  - 年柱切换：5.1.1 干支纪年 - 以立春为年界
  - 月柱切换：5.1.2 干支纪月 - 以节气（节）为月界
  - 日柱计算：5.1.3 干支纪日 - 子时为日界（标准未明确夜子时，本库按民俗共识作工程化扩展）
- 天文数据源：节气时刻采用寿星天文历（sxtwl），符合标准第 4.2 节“节气计算”的要求；基准时区采用 UTC+8（北京/香港）。

Standards: References GB/T 33661-2017. Solar-term instants via sxtwl in UTC+8; results are exposed through a cnlunar-compatible API.

### 核心算法口径 · Core Algorithm Rules
| 要素         | 中文规则                                                                 | English Rule                                                                 |
|--------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| 年柱         | 立春交节时刻后立即切换新年柱（精确到秒）                                 | Year pillar switches immediately after Lìchūn (Beginning of Spring)        |
| 月柱         | 仅当“节”类节气交节后切换月柱（排除“中气”）                               | Month pillar switches only after “Jié” solar terms (excluding “Zhongqi”)   |
| 日柱         | 23:00 起算次日日柱；23:00–23:59 期间对象整体按次日口径呈现               | Day pillar starts next day at 23:00; 23:00–23:59 uses next-day state       |
| 时区处理     | 裁边判断使用 `rule_tz` 时区；输出使用 `tz` 时区                          | Boundary checks use `rule_tz`; output uses `tz` timezone                   |

—

### 作者与动机 · Author & Motivation

- 作者身份：AI 与周易领域的执业人员，长期从事实务排盘与算法评估。
- 动机：在实践中发现现有库在“年柱/月柱/日柱边界、夜子时处理”上存在口径不一致与割裂体验的问题，因此实现一个“可解释、可验证、与民俗用法一致”的严格口径替代方案。

Author note: The author practices AI-driven Zhouyi applications. Practical discrepancies were observed in existing libraries regarding Gan-Zhi boundaries and night-hour handling; hence this project provides a stricter, explainable, and verifiable approach.

—

### 术语与口径 · Terminology & Conventions
（中文为准 / Chinese authoritative）
- 立春（Lìchūn, Beginning of Spring）：二十四节气之一，用作“年柱”的分界。
- 节（Jié）：用于“换月柱”的节气子集（不包括“中气”）。
- 中气（Zhongqi）：非“换月柱”依据（如秋分），用于天文划分但不触发月柱变更。
- 夜子时（Late Zishi, 23:00–23:59）：从 23:00 起算为“次日的日柱”；并为避免信息割裂，对象整体以前滚的“次日口径”呈现。

English notes: Lìchūn as year boundary; Jié terms for month change (not Zhongqi); treat 23:00–23:59 as next day as a whole.

—

### 验证与可复现 · Validation & Reproducibility
- 边界测试：节气交节时刻 ±60 秒验证；
- 跨日测试：22:59/23:00/23:59/00:30 一致性；
- 参考数据：权威年历与 sxtwl 双重对照；
- 用例覆盖：见 `tests/test_boundaries.py`；另附《标准化合规说明》。

See also: `docs/STANDARD_COMPLIANCE.md` for GB/T 33661-2017 mapping.

—

### 文件结构 · Repository Structure
```
.
├─ src/
│  └─ tungshing/
│     ├─ __init__.py          # 包导出 / Package exports
│     ├─ __main__.py          # CLI 入口 / CLI entry point
│     └─ core.py              # 核心实现 / Core implementation
├─ tests/
│  └─ test_boundaries.py      # 边界与口径用例 / Boundary tests
├─ docs/
│  └─ STANDARD_COMPLIANCE.md  # 国标合规说明 / Standard compliance notes
├─ .github/
│  └─ workflows/
│     └─ ci.yml               # CI 工作流 / CI workflow
├─ TungShing.py               # 兼容旧入口 / Backward-compat entry
├─ README.md
├─ CHANGELOG.md
├─ CONTRIBUTING.md
├─ LICENSE
├─ pyproject.toml
└─ .gitignore
```

—

### 安装 · Installation
```bash
pip install tungshing
```
- Python >= 3.9（使用内置 `zoneinfo`）
- Windows 会自动安装 `tzdata`
- 依赖：`cnlunar`, `sxtwl`

—

### 快速上手 · Quick Start
```python
from datetime import datetime
from zoneinfo import ZoneInfo
from tungshing import TungShing

dt = datetime(2025, 2, 3, 22, 11, tzinfo=ZoneInfo("Asia/Shanghai"))
ts = TungShing(dt)

print(ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char)
print(ts.lunarYear, ts.lunarMonth, ts.lunarDay, ts.lunarDayCn)
print("今日交节(规则时区)", ts.termTodayExact_ruleTz)
```
CLI:
```bash
tungshing --datetime "2025-02-03T22:11:00+08:00" --tz Asia/Shanghai --rule-tz Asia/Shanghai
```

—

### API 说明 · API
```python
TungShing(date: datetime | None = None, *, tz: str = "Asia/Shanghai", rule_tz: str = "Asia/Shanghai", **kwargs)
```
- date：输入时间（naive/aware 均可）；
- tz：输出与底层 `cnlunar` 的本地口径；
- rule_tz：严格裁边所采用的规则时区；
- 其它 `**kwargs` 原样传入 `cnlunar.Lunar`（如 `godType='8char'`, `year8Char='beginningOfSpring'`）。

采用严格口径重算：`year8Char`, `month8Char`, `day8Char`；其余字段由底层对象转发。

返回字段（与 `cnlunar.Lunar` 保持一致，按版本可能略有差异）：
- `lunarYear`, `lunarMonth`, `lunarDay`, `lunarYearCn`, `lunarMonthCn`, `lunarDayCn`
- `twohour8Char`（沿用原库口径）
- 严格口径：`year8Char`, `month8Char`, `day8Char`
- 便捷字段：`termTodayExact_ruleTz`, `termTodayExact_cn8`

—

### 与 cnlunar / sxtwl 的差异与动机
（中文为准 / Chinese authoritative）
- cnlunar：API 完整，但年/月/日口径在版本/参数之间存在不一致；
- sxtwl：天文口径准确，但非 cnlunar 兼容 API；
- 本库：以 sxtwl 为“裁边事实”，以 cnlunar API 提供结果，兼顾准确性与可用性。

—

### 开发与测试 · Dev & Test
- 可选开发依赖：`pip install pytest build twine`
- 运行测试：`pytest -q`
- 本地打包：`python -m build`（生成 `dist/`）
- 包校验：`python -m twine check dist/*`
- CI：见 `.github/workflows/ci.yml`（push/PR 自动触发）

—

### 变更日志 · Changelog
- 详见 `CHANGELOG.md`
  - 当前版本：`tungshing.__version__`（从包元数据导出）

—

### 致谢与引用 · Acknowledgements & References
- GB/T 33661-2017《农历的编算和颁行》
- 寿星天文历（sxtwl）
- cnlunar

—

### 贡献与反馈 · Contributing
- Issue: `https://github.com/xianyu564/tungshing/issues`
- PR: `https://github.com/xianyu564/tungshing/pulls`
- Email: z_zz@u.nus.edu

—

### 许可证 · License
MIT License © 2025 张衔瑜/张子阳


