# GB/T 33661-2017 合规性说明 · Standard Compliance

中文为准；英文为补充说明（Chinese is authoritative; English notes included）

## 第 5.1 条款实现对照表 · Clause 5.1 Mapping
| 标准条款 | 本库实现要点 | 验证方法 |
|---|---|---|
| 5.1.1 干支纪年（以立春为年界） | 立春交节后立即切换年柱（秒级） | 立春时刻 ±60s 切换测试 |
| 5.1.2 干支纪月（以节为月界） | 仅在“节”交节后切换月柱；“中气”不触发 | 24 节气分界测试；对照惊蛰/立秋/立冬等 |
| 5.1.3 干支纪日（子时为日界） | 23:00 起算次日日柱；23:00–23:59 对象整体以前滚的“次日口径” | 22:59/23:00/23:59/00:30 一致性测试 |

Notes:
- GB/T 33661-2017 未明确“夜子时”工程化处理。本库依据民俗共识与实务排盘需要作出扩展：从 23:00 起作为“次日”，且 23:00–23:59 期间对象整体按“次日口径”呈现，避免“干支已切但农历纪日/宜忌未联动”的割裂体验。
- English: The standard does not prescribe engineering details for late Zishi (23:00–23:59). We adopt a practical convention widely accepted in folk practices: start the next day from 23:00 and forward the whole object state during 23:00–23:59.

## 天文计算依据 · Astronomical Basis
- 节气计算：采用寿星天文历（sxtwl），符合标准第 4.2 节“节气计算”的要求；
- 基准时区：UTC+8（北京/香港）；
- 精度：秒级（满足标准第 4.3 节精度要求）。

## 交叉验证 · Cross-Validation
- 以权威年历（如中国科学院紫金山天文台《天文年历》）对照节气交节时刻；
- 以 sxtwl 计算输出进行二次比对；
- 在边界前后 ±60 秒验证年/月柱切换；
- 夜子时段进行对象整体一致性验证（与次日 00:30 对齐）。
