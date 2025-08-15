# -*- coding: utf-8 -*-
"""
严格口径的 cnlunar“替身”
- 年柱：立春分界（分秒级）
- 月柱：以“节”交节时刻分界（分秒级）
- 日柱：晚子时=23:00 起算“次日”的日柱
其余字段/方法：与原 cnlunar 完全一致（通过转发）。
节气时刻以 HKO/Beijing(UTC+8) 口径。
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Any
from zoneinfo import ZoneInfo

import cnlunar as _cn
import sxtwl as _sx


GAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
ZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
JQMC = [
    "冬至","小寒","大寒","立春","雨水","惊蛰","春分","清明","谷雨",
    "立夏","小满","芒种","夏至","小暑","大暑","立秋","处暑","白露",
    "秋分","寒露","霜降","立冬","小雪","大雪",
]
_JIE_IDX = {JQMC.index(n) for n in [
    "立春","惊蛰","清明","立夏","芒种","小暑",
    "立秋","白露","寒露","立冬","大雪","小寒",
]}  # 以“节”而非“中气”换月


def _gz_str(gz) -> str:
    return GAN[gz.tg] + ZHI[gz.dz]


def _to_local(dt: datetime, tz: str) -> datetime:
    z = ZoneInfo(tz)
    return (dt if dt.tzinfo else dt.replace(tzinfo=z)).astimezone(z)


def _aware_to_naive(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None)


def _term_on_day_in_rule_tz(y: int, m: int, d: int, rule_tz: str):
    """
    若该（rule_tz 口径的）公历日有节气：
      返回 (节气名, 交节时刻@rule_tz[aware], 交节时刻@UTC+8[aware])
    否则 None
    说明：_sx.JD2DD 输出按 UTC+8 给“年月日时分秒”，再转到 rule_tz。
    """
    day = _sx.fromSolar(y, m, d)
    if not day.hasJieQi():
        return None
    k = day.getJieQi()
    name = JQMC[k]
    t = _sx.JD2DD(day.getJieQiJD())
    cn8 = datetime(int(t.Y), int(t.M), int(t.D), int(t.h), int(t.m), 0,
                   tzinfo=ZoneInfo("Asia/Shanghai")) + timedelta(seconds=float(t.s))
    return (name, cn8.astimezone(ZoneInfo(rule_tz)), cn8)


class TungShing:
    """
    与 cnlunar.Lunar 同名同用法的“严格口径”包装器：
      - 位置参数/关键字参数与原类保持兼容（date, godType='8char', year8Char=...）
      - 额外可选 keyword：tz（输出/原库口径，默认 'Asia/Shanghai'）、
                         rule_tz（裁边口径，默认 'Asia/Shanghai'）
      - 属性与方法：除 year8Char/month8Char/day8Char 采“严格口径”

      夜子时(23:00–23:59)：且农历日数字在 23:00 同步滚动，
      整对象以“次日口径”转发（__getattr__ → 次日 _forward）
    """
    def __init__(self, date: datetime = None, *args, **kwargs):
        if date is None:
            date = datetime.now()

        self._tz = kwargs.pop("tz", "Asia/Shanghai")
        self._rule_tz = kwargs.pop("rule_tz", "Asia/Shanghai")

        dt_local = _to_local(date, self._tz)              # aware@tz
        dt_naive = _aware_to_naive(dt_local)              # naive@tz
        self._base = _cn.Lunar(dt_naive, *args, **kwargs) # 保持原库参数兼容
        self.date = self._base.date

        dt_rule = _to_local(date, self._rule_tz)          # aware@rule_tz
        dt_rule_naive = _aware_to_naive(dt_rule)
        y8, m8, d8, hh8 = dt_rule.year, dt_rule.month, dt_rule.day, dt_rule.hour

        self._forward = self._base
        if hh8 == 23:
            alt_naive = _aware_to_naive(dt_local + timedelta(hours=1))
            self._forward = _cn.Lunar(alt_naive, *args, **kwargs)

        self.year8Char = self._calc_year_gz_strict(y8, dt_rule_naive)
        self.month8Char = self._calc_month_gz_strict(y8, m8, d8, dt_rule_naive)
        self.day8Char = self._calc_day_gz_strict(hh8, dt_local, dt_naive)
        self.twohour8Char = self._base.twohour8Char

        src = self._forward
        self.lunarYear = src.lunarYear
        self.lunarMonth = src.lunarMonth
        self.lunarDay = src.lunarDay
        if hasattr(src, "isLunarLeapMonth"):
            self.isLunarLeapMonth = src.isLunarLeapMonth
        if hasattr(src, "lunarIsLeapMonth"):
            self.lunarIsLeapMonth = src.lunarIsLeapMonth
        self.lunarYearCn = src.lunarYearCn
        self.lunarMonthCn = src.lunarMonthCn
        self.lunarDayCn = src.lunarDayCn

    def _calc_year_gz_strict(self, y: int, dt_rule_naive: datetime) -> str:
        lichun = None
        for md in [(2, 3), (2, 4), (2, 5)]:
            info = _term_on_day_in_rule_tz(y, md[0], md[1], self._rule_tz)
            if info and info[0] == "立春":
                lichun = info
                break
        if lichun:
            _, lc_rule_aware, _ = lichun
            passed = dt_rule_naive >= _aware_to_naive(lc_rule_aware)
            y_curr = _gz_str(_sx.fromSolar(y, 7, 1).getYearGZ())
            y_prev = _gz_str(_sx.fromSolar(y - 1, 7, 1).getYearGZ())
            return y_curr if passed else y_prev
        return self._base.year8Char

    def _calc_month_gz_strict(self, y: int, m: int, d: int, dt_rule_naive: datetime) -> str:
        day_obj = _sx.fromSolar(y, m, d)
        mgz = _gz_str(day_obj.getMonthGZ())
        if day_obj.hasJieQi():
            k = day_obj.getJieQi()
            info = _term_on_day_in_rule_tz(y, m, d, self._rule_tz)
            if info:
                _, t_rule, _ = info
                if (k in _JIE_IDX) and dt_rule_naive < _aware_to_naive(t_rule):
                    mgz = _gz_str(day_obj.before(1).getMonthGZ())
        return mgz

    def _calc_day_gz_strict(self, hour_rule: int,
                            dt_local_aware: datetime,
                            dt_naive_for_base: datetime) -> str:
        base = self._base.day8Char
        if hour_rule == 23:
            alt_naive = _aware_to_naive(dt_local_aware + timedelta(hours=1))
            alt = _cn.Lunar(alt_naive, godType='8char', year8Char='beginningOfSpring')
            return alt.day8Char if alt.day8Char != base else base
        return base

    def __getattr__(self, name: str) -> Any:
        return getattr(self._forward, name)

    @property
    def termTodayExact_ruleTz(self) -> Optional[str]:
        y, m, d = _to_local(self.date, self._rule_tz).date().timetuple()[:3]
        info = _term_on_day_in_rule_tz(y, m, d, self._rule_tz)
        return info[1].isoformat() if info else None

    @property
    def termTodayExact_cn8(self) -> Optional[str]:
        y, m, d = _to_local(self.date, self._rule_tz).date().timetuple()[:3]
        info = _term_on_day_in_rule_tz(y, m, d, self._rule_tz)
        return info[2].isoformat() if info else None


