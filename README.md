# TungShing · 严格口径的黄历/通胜

[![CI](https://github.com/xianyu564/tungshing/actions/workflows/ci.yml/badge.svg)](https://github.com/xianyu564/tungshing/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tungshing.svg)](https://pypi.org/project/tungshing/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)](#)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org)

> **严格口径的中国农历黄历库，兼容 cnlunar API | Strict Chinese lunisolar calendar library with cnlunar-compatible API**

TungShing（通胜）是"黄历"的别名；黄历属于中国传统的"阴阳合历（Lunisolar Calendar）"。本库严格遵循 **GB/T 33661-2017《农历的编算和颁行》** 国家标准，以 sxtwl 天文算法为基础，提供兼容 cnlunar 的 API 接口。

*TungShing (aka Tung Shing/通胜) is an alias of the Chinese Huangli (traditional lunisolar almanac). This library strictly follows the **GB/T 33661-2017** national standard, based on sxtwl astronomical algorithms, and provides a cnlunar-compatible API.*

## ✨ 主要特性 · Key Features

- 🎯 **严格口径**: 年柱立春、月柱按节、日柱晚子时，完全符合国标
- 📏 **标准合规**: 严格遵循 GB/T 33661-2017 国家标准
- 🔄 **API兼容**: 与 cnlunar 兼容的 API 设计
- ⚡ **高精度**: 基于 sxtwl 天文算法，确保计算准确性  
- 🐍 **现代Python**: 支持 Python 3.9+，类型提示完整
- 🧪 **高质量**: 完整测试覆盖，CI/CD 保障

*Strict standards compliance • cnlunar-compatible API • High precision • Modern Python • Quality assured*

---

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

#### 基础用法 · Basic Usage

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from tungshing import TungShing

# 使用当前时间 · Current time
ts = TungShing()
print(f"当前四柱: {ts.year8Char} {ts.month8Char} {ts.day8Char} {ts.twohour8Char}")
print(f"农历: {ts.lunarYearCn}年{ts.lunarMonthCn}月{ts.lunarDayCn}")

# 指定时间 · Specific datetime
dt = datetime(2025, 2, 3, 22, 11, tzinfo=ZoneInfo("Asia/Shanghai"))
ts = TungShing(dt)
print(f"八字: {ts.year8Char} {ts.month8Char} {ts.day8Char} {ts.twohour8Char}")
print(f"农历: {ts.lunarYear}年{ts.lunarMonth}月{ts.lunarDay}日 ({ts.lunarDayCn})")
```

#### 严格边界验证 · Strict Boundary Validation

```python
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 立春前后年柱变化 · Year pillar change at Lichun
lichun_2025 = datetime(2025, 2, 3, 22, 10, 13, tzinfo=ZoneInfo("Asia/Shanghai"))

before_lichun = TungShing(lichun_2025 - timedelta(minutes=1))
after_lichun = TungShing(lichun_2025 + timedelta(minutes=1))

print(f"立春前年柱: {before_lichun.year8Char}")  # 甲辰 (2024年)
print(f"立春后年柱: {after_lichun.year8Char}")   # 乙巳 (2025年)

# 节气换月柱 · Month pillar change at Jie terms
jingzhe_2025 = datetime(2025, 3, 5, 16, 7, tzinfo=ZoneInfo("Asia/Shanghai"))

before_jingzhe = TungShing(jingzhe_2025 - timedelta(minutes=1))
after_jingzhe = TungShing(jingzhe_2025 + timedelta(minutes=1))

print(f"惊蛰前月柱: {before_jingzhe.month8Char}")
print(f"惊蛰后月柱: {after_jingzhe.month8Char}")

# 夜子时日柱前滚 · Day pillar advance at night Zi hour
night_zi = datetime(2025, 1, 1, 23, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
ts_night = TungShing(night_zi)

print(f"23:30日柱: {ts_night.day8Char}")      # 次日日柱
print(f"23:30农历: {ts_night.lunarDayCn}")    # 次日农历
```

#### 时区处理 · Timezone Handling

```python
# 不同时区的边界计算 · Different timezone boundaries
hk_time = datetime(2025, 2, 3, 22, 10, tzinfo=ZoneInfo("Asia/Hong_Kong"))
sh_time = datetime(2025, 2, 3, 22, 10, tzinfo=ZoneInfo("Asia/Shanghai"))

ts_hk = TungShing(hk_time, tz="Asia/Hong_Kong", rule_tz="Asia/Hong_Kong")
ts_sh = TungShing(sh_time, tz="Asia/Shanghai", rule_tz="Asia/Shanghai")

print(f"香港时区年柱: {ts_hk.year8Char}")
print(f"上海时区年柱: {ts_sh.year8Char}")
```

#### CLI 使用 · Command Line Usage

```bash
# 当前时间查询 · Current time
tungshing

# 指定时间查询 · Specific time
tungshing --datetime "2025-02-03T22:11:00+08:00"

# 不同时区 · Different timezones  
tungshing --datetime "2025-02-03T15:11:00Z" --tz "Asia/Shanghai" --rule-tz "Asia/Hong_Kong"

# 查看帮助 · Help
tungshing --help
```

#### 节气查询 · Solar Term Queries

```python
# 查询今日是否有节气 · Check for solar terms today
ts = TungShing(datetime(2025, 2, 3, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai")))

if ts.termTodayExact_ruleTz:
    print(f"今日节气时刻: {ts.termTodayExact_ruleTz}")
    print(f"北京时间: {ts.termTodayExact_cn8}")
else:
    print("今日无节气")
```

#### 与 cnlunar 兼容性 · cnlunar Compatibility

```python
# 完全兼容 cnlunar.Lunar 的参数和属性 · Full cnlunar.Lunar compatibility
ts = TungShing(
    datetime(2025, 1, 1),
    godType='8char',
    year8Char='beginningOfSpring'
)

# 所有 cnlunar 属性都可访问 · All cnlunar attributes accessible
print(ts.lunarYear, ts.lunarMonth, ts.lunarDay)
print(ts.lunarYearCn, ts.lunarMonthCn, ts.lunarDayCn)

# 但年柱、月柱、日柱使用严格口径 · But with strict timing for pillars
print("严格口径四柱:", ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char)
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


