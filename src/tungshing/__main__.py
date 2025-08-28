"""
TungShing command-line interface.

Provides a convenient CLI for querying Chinese lunar calendar information
with strict timing accuracy according to GB/T 33661-2017 standards.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from .core import TungShing


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="tungshing",
        description=(
            "TungShing CLI - 严格口径的黄历/通胜\n"
            "Strict Chinese lunar calendar with GB/T 33661-2017 compliance"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tungshing                                    # Current time
  tungshing --datetime 2025-02-03T22:11:00+08:00
  tungshing --datetime 2025-02-03T22:11:00 --tz Asia/Shanghai
  tungshing --tz UTC --rule-tz Asia/Hong_Kong

For more information: https://github.com/xianyu564/tungshing
        """
    )
    parser.add_argument(
        "--datetime",
        dest="dt",
        metavar="DATETIME",
        help=(
            "ISO datetime string (e.g., 2025-02-03T22:11:00+08:00)\n"
            "If timezone not specified, uses --tz value"
        ),
    )
    parser.add_argument(
        "--tz",
        dest="tz",
        default="Asia/Shanghai",
        metavar="TIMEZONE",
        help="Output/local timezone (default: Asia/Shanghai)",
    )
    parser.add_argument(
        "--rule-tz",
        dest="rule_tz",
        default="Asia/Shanghai", 
        metavar="TIMEZONE",
        help="Boundary calculation timezone (default: Asia/Shanghai)",
    )
    parser.add_argument(
        "--version",
        action="version", 
        version=f"%(prog)s {get_version()}"
    )
    
    args = parser.parse_args()

    # Parse datetime
    if args.dt:
        try:
            dt = datetime.fromisoformat(args.dt)
        except ValueError as e:
            parser.error(f"Invalid --datetime format: {e}\nUse ISO 8601 format like: 2025-02-03T22:11:00+08:00")
    else:
        dt = datetime.now(ZoneInfo(args.tz))

    # Create TungShing object and display results
    try:
        ts = TungShing(dt, tz=args.tz, rule_tz=args.rule_tz)
        
        print(f"{'='*60}")
        print(f"TungShing - 严格口径黄历 | Strict Lunar Calendar")
        print(f"{'='*60}")
        print(f"Reference time: {ts.date}")
        print(f"Timezone: {args.tz} | Rule timezone: {args.rule_tz}")
        print()
        
        print("四柱八字 | Four Pillars (Bazi):")
        print(f"  年柱 Year:   {ts.year8Char}")
        print(f"  月柱 Month:  {ts.month8Char}")
        print(f"  日柱 Day:    {ts.day8Char}")
        print(f"  时柱 Hour:   {ts.twohour8Char}")
        print()
        
        print("农历信息 | Lunar Calendar:")
        print(f"  农历日期: {ts.lunarYear}年 {ts.lunarMonth}月 {ts.lunarDay}日")
        print(f"  中文表示: {ts.lunarYearCn}年 {ts.lunarMonthCn}月 {ts.lunarDayCn}")
        print()
        
        # Solar term information
        if ts.termTodayExact_ruleTz:
            print("今日节气 | Solar Term Today:")
            print(f"  规则时区: {ts.termTodayExact_ruleTz}")
            print(f"  北京时间: {ts.termTodayExact_cn8}")
        else:
            print("今日无节气 | No solar term today")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def get_version() -> str:
    """Get package version."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"


if __name__ == "__main__":
    main()


