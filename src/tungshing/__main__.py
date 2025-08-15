from __future__ import annotations

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from .core import TungShing


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "TungShing CLI (Chinese authoritative; English note: a strict Huangli/Tung Shing)"
        )
    )
    parser.add_argument(
        "--datetime",
        dest="dt",
        help=(
            "ISO datetime, 例如 2025-02-03T22:11:00+08:00 / English: ISO datetime, e.g. 2025-02-03T22:11:00+08:00"
        ),
    )
    parser.add_argument(
        "--tz",
        dest="tz",
        default="Asia/Shanghai",
        help=(
            "输出/本地时区（默认 Asia/Shanghai）/ English: output/local tz (default: Asia/Shanghai)"
        ),
    )
    parser.add_argument(
        "--rule-tz",
        dest="rule_tz",
        default="Asia/Shanghai",
        help=(
            "裁边规则时区（默认 Asia/Shanghai）/ English: boundary tz (default: Asia/Shanghai)"
        ),
    )
    args = parser.parse_args()

    if args.dt:
        try:
            dt = datetime.fromisoformat(args.dt)
        except Exception:
            raise SystemExit("Invalid --datetime format. Use ISO 8601, e.g. 2025-02-03T22:11:00+08:00")
    else:
        dt = datetime.now(ZoneInfo(args.tz))

    ts = TungShing(dt, tz=args.tz, rule_tz=args.rule_tz)
    print("date:", ts.date)
    print("year8Char:", ts.year8Char)
    print("month8Char:", ts.month8Char)
    print("day8Char:", ts.day8Char)
    print("twohour8Char:", ts.twohour8Char)
    print("lunar:", ts.lunarYear, ts.lunarMonth, ts.lunarDay, ts.lunarDayCn)
    print("termTodayExact_ruleTz:", ts.termTodayExact_ruleTz)
    print("termTodayExact_cn8:", ts.termTodayExact_cn8)


if __name__ == "__main__":
    main()


