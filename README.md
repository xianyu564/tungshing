### TungShing · 严格口径的黄历/通胜（兼容 cnlunar 用法）

TungShing（通胜）是“黄历”的别名；黄历属于中国传统的“阴阳合历（Lunisolar Calendar）”。本文档以中文为准，同时提供必要的英文说明（Chinese is authoritative; English notes are provided for convenience）。

TungShing (aka Tung Shing/通胜) is an alias of the Chinese Huangli (traditional lunisolar almanac). Chinese text in this README is authoritative; English summaries are included for international users.

—

**TungShing** 提供“严谨口径”的干支口径与夜子时处理：

- **年柱**：以“立春”分界，并精确到分秒
- **月柱**：以“节”交节时刻分界（而非中气），并精确到分秒
- **日柱**：按“晚子时=23:00 起算次日的日柱”；同时为了保持整体一致，23:00–23:59 将对象整体按“次日口径”转发
- 其余属性/方法尽量保持与 `cnlunar.Lunar` 一致（通过转发）

#### 方法口径（重申）

- 年柱：立春之后即切换到新年柱（到分秒级边界为准）。
- 月柱：仅在“节”交节之后切换月柱（不是“中气”）。
- 日柱：23:00 起算次日的日柱；且 23:00–23:59 期间整体视为“次日口径”，农历日数字、中文纪日、当日宜忌等同步前滚。

English (Chinese authoritative):
- Year pillar switches right after Lìchūn (minute-second precision).
- Month pillar switches only at Jié solar terms (not at Zhongqi), with minute-second precision.
- Day pillar starts the next day from 23:00; during 23:00–23:59 the object forwards to the next-day state as a whole.

—

### 作者与动机 · Author & Motivation

- 作者身份：AI 与周易领域的执业人员，长期从事实务排盘与算法评估。
- 动机：在实践中发现现有库在“年柱/月柱/日柱边界、夜子时处理”上存在口径不一致与割裂体验的问题，因此实现一个“可解释、可验证、与民俗用法一致”的严格口径替代方案。

Author note: The author practices AI-driven Zhouyi applications. Practical discrepancies were observed in existing libraries regarding Gan-Zhi boundaries and night-hour handling; hence this project provides a stricter, explainable, and verifiable approach.

—

### 标准依据与科学基础 · Standards & Scientific Basis

- 严格遵循：GB/T 33661-2017《农历的编算和颁行》（国家质量监督检验检疫总局、国家标准化管理委员会）作为根本依据；
- 天文口径：节气交节时刻基于寿星天文历（sxtwl），并以北京/香港时间（UTC+8）作为标准口径；
- 工程实现：在保持 `cnlunar` API 易用性的前提下，以 `sxtwl` 的节气与干支基线作为“裁边事实”。

Standards: This project references GB/T 33661-2017 (Compilation and Promulgation of the Chinese Calendar) for normative guidance. Solar term instants rely on sxtwl, interpreted in UTC+8; results are presented via a cnlunar-compatible API.

—

### 术语与口径 · Terminology & Conventions

（中文为准 / Chinese authoritative）

- 立春（Lìchūn, Beginning of Spring）：二十四节气之一，用作“年柱”的分界。
- 节（Jié）：用于“换月柱”的节气子集（不包括“中气”）。
- 中气（Zhongqi）：非“换月柱”依据（如秋分），用于天文划分但不触发月柱变更。
- 夜子时（Late Zishi, 23:00–23:59）：从 23:00 起算为“次日的日柱”；并为避免信息割裂，对象整体以前滚的“次日口径”呈现。

English notes:
- Lìchūn is used as the year-pillar boundary; Jié terms for month-pillar change; Zhongqi terms do not change the month pillar. Night hours 23:00–23:59 are treated as the next day as a whole.

—

### 验证与可复现 · Validation & Reproducibility

- 交叉验证：
  - 使用 `sxtwl` 获取交节精确时刻（UTC+8），与 GB/T 33661-2017 的口径一致；
  - 检查临界分钟前后（±60s）年/月柱是否按预期切换；
  - 夜子时（23:00–23:59）对比“当日 22:59”与“次日 00:30”的一致性。
- 本仓库提供关键用例（`tests/test_boundaries.py`）覆盖：
  - 立春前后换年柱；
  - 惊蛰/立秋/立冬等“节”触发换月柱；
  - 秋分（中气）不触发换月柱；
  - 23:00–23:59 整体前滚一致性。

English notes: Tests cover second-level boundaries around Lìchūn and specific Jié terms, plus non-switching at Zhongqi (equinox/solstice where applicable), and night-hour forwarding consistency checks.

—

### 路线图 · Roadmap

- 增加更多官方权威数据校验点与年份覆盖；
- 提供更详尽的命令行输出（例如交节名与时刻的多时区对照）；
- 增加其它民俗口径的可选开关（保持默认值为“严格口径”）。

依赖 `cnlunar` 与 `sxtwl`：前者用于原有 API 与多数计算，后者用于节气/干支边界的精准判定。

---

### 安装

```bash
pip install tungshing
```

Python 版本要求：>= 3.9（使用内置 `zoneinfo`）。

---

### 快速上手

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

命令行：

```bash
tungshing --datetime "2025-02-03T22:11:00+08:00" --tz Asia/Shanghai --rule-tz Asia/Shanghai
```

---

### 与 cnlunar / sxtwl 的差异与动机

- **cnlunar**：
  - 优点：API 完整、实用字段多、生态广。
  - 疑点：
    - 年柱是否以“立春”为界、如何在分秒级边界处切换，不同版本与参数存在差异；
    - 月柱是否按“节”或“中气”切换，口径不一；
    - 日柱与“夜子时（23:00–23:59）”的关系不统一，常出现“日柱切了但农历数字/宜忌未联动”的割裂体验。
- **sxtwl**（寿星天文历）：
  - 优点：节气时刻与干支基线更贴近天文口径，能获取精准交节时刻。
  - 局限：并非以“兼容 cnlunar 的 API”作为目标库，直接使用时需要自己拼装周边信息与口径转换。

TungShing 以 `sxtwl` 的节气和干支基线为“精确裁边依据”，并将结果以 `cnlunar.Lunar` 的 API 暴露：

- 年柱严格以“立春”分界；
- 月柱严格以“节”交节分界（不是“中气”）；
- 日柱在“晚子时 23:00 起算次日”；
- 23:00–23:59 之间，为了使农历日数字、中文纪日、当日宜忌等“整体”一致，对象会整体以前滚的“次日口径”转发。

这让口径既“严谨可解释”，又“保留 cnlunar 的易用接口”。

#### 为何说“cnlunar 和 sxtwl 还不够合理”？

- **非同一口径导致的边界错觉**：常见“年柱/月柱切换点”在不同库或不同参数下不一致，用户很难确认“到底以什么为准”。
- **日柱与夜子时的分离**：很多实现只改“日柱”，但不让农历数字/中文纪日/日宜忌整体联动，用户看到的信息彼此打架。
- **缺少统一的可解释规则**：当遇到分秒级边界（如立春当分钟）时，如何判定，缺少既能对齐天文事实又能对齐民俗用法的明确方案。

TungShing 的原则：

- 将“严格裁边”交由 `sxtwl` 的节气与干支基线；
- 以“立春/节/晚子时”明确三大关键规则；
- 以“前滚转发”机制保证 23:00–23:59 期间整体一致；
- 最终以 `cnlunar` 的 API 对外，兼容生态，便于迁移与对比验证。

English (Chinese authoritative):
- cnlunar offers a rich API but exhibits boundary inconsistencies across versions/configs (year at Lìchūn, month at Jié vs. Zhongqi, night-hour handling), leading to user confusion.
- sxtwl provides accurate astronomical baselines (solar terms, Gan-Zhi), but is not an API-compatible drop-in for cnlunar.
- TungShing uses sxtwl for strict boundaries and presents results through cnlunar-like APIs, thus combining accuracy with usability.

---

### API 说明

```python
TungShing(date: datetime | None = None, *, tz: str = "Asia/Shanghai", rule_tz: str = "Asia/Shanghai", **kwargs)
```

- **date**：输入时间。可以为 naive（将按 tz 解释）或 aware。
- **tz**：输出与底层 `cnlunar` 的本地口径（默认 `Asia/Shanghai`）。
- **rule_tz**：严格裁边所采用的规则时区（默认 `Asia/Shanghai`）。
- 其它 `**kwargs` 将原样传入 `cnlunar.Lunar`（例如 `godType='8char'`, `year8Char='beginningOfSpring'` 等）。

可用属性（与 `cnlunar.Lunar` 对齐）：`lunarYear`, `lunarMonth`, `lunarDay`, `lunarYearCn`, `lunarMonthCn`, `lunarDayCn`, `twohour8Char`, 以及众多原有字段。以下字段采用“严格口径”重算：`year8Char`, `month8Char`, `day8Char`。

附加便捷字段：

- `termTodayExact_ruleTz`: 今日若有交节，返回规则时区的精确交节时刻 ISO 字符串；否则为 `None`
- `termTodayExact_cn8`: 今日若有交节，返回 UTC+8 口径（北京/香港）的精确交节时刻 ISO 字符串；否则为 `None`

---

### 时区与“夜子时”

- “严格裁边（年/月/日柱的边界判断）”使用 `rule_tz`；
- “原库本地计算与输出”使用 `tz`；
- “晚子时=23:00 起算次日日柱”，且 23:00–23:59 期间对象整体前滚，使数字与纪日等对齐。

---

### 开发与测试

可选：开发依赖

```bash
pip install pytest
```

运行测试：

```bash
pytest -q
```

CI 会在多个 Python 版本上运行边界用例。

关于 CI：本仓库已包含 GitHub Actions 工作流文件 `.github/workflows/ci.yml`，在 `main/master` 分支的 push 与 PR 时自动触发，安装依赖并执行 `pytest -q`。如需修改 Python 版本矩阵或步骤，请编辑该文件。

---

### 贡献与反馈

欢迎通过 Issue/PR 反馈问题与改进建议：

- Issue: `https://github.com/xianyu564/tungshing/issues`
- PR: `https://github.com/xianyu564/tungshing/pulls`

提交前请先运行本地测试，确保口径未被破坏。

---

### 许可证

MIT License © 2025 张衔瑜/张子阳


