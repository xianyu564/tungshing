"""
Advanced interactive CLI for TungShing with enhanced features.

This module provides a sophisticated command-line interface with:
- Interactive mode for exploring different dates
- Beautiful formatting and colors
- Performance benchmarking
- Batch processing capabilities
- Export functionality
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from .core import TungShing
from .cache import get_cache_stats, clear_all_caches, optimize_memory
from .validation import TungShingValidator, TungShingError


class Colors:
    """ANSI color codes for terminal output."""
    
    # Text colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text if terminal supports it."""
        if sys.stdout.isatty():
            return f"{color}{text}{cls.RESET}"
        return text
    
    @classmethod
    def success(cls, text: str) -> str:
        """Format success message."""
        return cls.colorize(f"✓ {text}", cls.GREEN)
    
    @classmethod
    def error(cls, text: str) -> str:
        """Format error message."""
        return cls.colorize(f"✗ {text}", cls.RED)
    
    @classmethod
    def warning(cls, text: str) -> str:
        """Format warning message."""
        return cls.colorize(f"⚠ {text}", cls.YELLOW)
    
    @classmethod
    def info(cls, text: str) -> str:
        """Format info message."""
        return cls.colorize(f"ℹ {text}", cls.BLUE)
    
    @classmethod
    def header(cls, text: str) -> str:
        """Format header text."""
        return cls.colorize(text, cls.BOLD + cls.CYAN)
    
    @classmethod
    def dim(cls, text: str) -> str:
        """Format dimmed text."""
        return cls.colorize(text, cls.DIM)


class TungShingCLI:
    """
    Advanced command-line interface for TungShing.
    
    Provides interactive features, beautiful formatting, and
    comprehensive functionality for exploring Chinese calendar data.
    """
    
    def __init__(self):
        """Initialize CLI interface."""
        self.colors = Colors()
        self.validator = TungShingValidator()
    
    def format_header(self, title: str, width: int = 80) -> str:
        """Create a beautifully formatted header."""
        border = "═" * width
        padding = (width - len(title) - 2) // 2
        header_line = f"║{' ' * padding}{title}{' ' * (width - len(title) - padding - 2)}║"
        
        return f"""╔{border}╗
{header_line}
╚{border}╝"""
    
    def format_tungshing_output(self, ts: TungShing, tz: str, rule_tz: str) -> str:
        """Format TungShing object output with beautiful styling."""
        output = []
        
        # Header
        header = "TungShing - 严格口径黄历 | Strict Lunar Calendar"
        output.append(self.colors.header(self.format_header(header)))
        output.append("")
        
        # Basic information
        output.append(self.colors.info("📅 Reference Information"))
        output.append(f"   Time: {self.colors.colorize(str(ts.date), Colors.CYAN)}")
        output.append(f"   Timezone: {self.colors.colorize(tz, Colors.YELLOW)} | Rule timezone: {self.colors.colorize(rule_tz, Colors.YELLOW)}")
        output.append("")
        
        # Four Pillars (Bazi)
        output.append(self.colors.info("🏛️  四柱八字 | Four Pillars (Bazi)"))
        pillars = [
            ("年柱 Year", ts.year8Char),
            ("月柱 Month", ts.month8Char),
            ("日柱 Day", ts.day8Char),
            ("时柱 Hour", ts.twohour8Char)
        ]
        
        for label, value in pillars:
            formatted_value = self.colors.colorize(value, Colors.MAGENTA + Colors.BOLD)
            output.append(f"   {label:12}: {formatted_value}")
        output.append("")
        
        # Lunar calendar information
        output.append(self.colors.info("🌙 农历信息 | Lunar Calendar"))
        output.append(f"   农历日期: {self.colors.colorize(f'{ts.lunarYear}年 {ts.lunarMonth}月 {ts.lunarDay}日', Colors.CYAN)}")
        output.append(f"   中文表示: {self.colors.colorize(f'{ts.lunarYearCn}年 {ts.lunarMonthCn}月 {ts.lunarDayCn}', Colors.GREEN)}")
        output.append("")
        
        # Solar term information
        if hasattr(ts, 'termTodayExact_ruleTz') and ts.termTodayExact_ruleTz:
            output.append(self.colors.info("🌅 今日节气 | Solar Term Today"))
            output.append(f"   规则时区: {self.colors.colorize(ts.termTodayExact_ruleTz, Colors.YELLOW)}")
            if hasattr(ts, 'termTodayExact_cn8') and ts.termTodayExact_cn8:
                output.append(f"   北京时间: {self.colors.colorize(ts.termTodayExact_cn8, Colors.YELLOW)}")
        else:
            output.append(self.colors.dim("📝 今日无节气 | No solar term today"))
        
        return "\n".join(output)
    
    def interactive_mode(self) -> None:
        """Start interactive exploration mode."""
        print(self.colors.header("🎯 TungShing Interactive Mode"))
        print(self.colors.info("Enter dates to explore, or 'help' for commands"))
        print(self.colors.dim("Press Ctrl+C to exit"))
        print()
        
        current_tz = "Asia/Shanghai"
        current_rule_tz = "Asia/Shanghai"
        
        while True:
            try:
                user_input = input(self.colors.colorize("TungShing> ", Colors.BLUE + Colors.BOLD)).strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self.show_interactive_help()
                elif user_input.lower() == 'cache':
                    self.show_cache_stats()
                elif user_input.lower() == 'clear':
                    clear_all_caches()
                    print(self.colors.success("Cache cleared"))
                elif user_input.lower().startswith('tz '):
                    new_tz = user_input[3:].strip()
                    try:
                        current_tz = self.validator.validate_timezone(new_tz)
                        print(self.colors.success(f"Timezone set to: {current_tz}"))
                    except Exception as e:
                        print(self.colors.error(f"Invalid timezone: {e}"))
                elif user_input.lower().startswith('rule_tz '):
                    new_rule_tz = user_input[8:].strip()
                    try:
                        current_rule_tz = self.validator.validate_timezone(new_rule_tz)
                        print(self.colors.success(f"Rule timezone set to: {current_rule_tz}"))
                    except Exception as e:
                        print(self.colors.error(f"Invalid rule timezone: {e}"))
                elif user_input.lower() == 'now':
                    self.process_datetime(datetime.now(), current_tz, current_rule_tz)
                elif user_input.lower() == 'benchmark':
                    self.run_benchmark()
                else:
                    # Try to parse as datetime
                    self.parse_and_process_datetime(user_input, current_tz, current_rule_tz)
            
            except KeyboardInterrupt:
                print("\n" + self.colors.info("Goodbye! 再见！"))
                break
            except EOFError:
                break
            except Exception as e:
                print(self.colors.error(f"Error: {e}"))
    
    def show_interactive_help(self) -> None:
        """Show help for interactive mode."""
        help_text = """
🎯 Interactive Mode Commands:

📅 Date/Time Input:
   now                    - Use current time
   2025-02-03            - Date (YYYY-MM-DD)
   2025-02-03T22:11:00   - Date and time
   2025-02-03T22:11:00+08:00 - With timezone

⚙️  Settings:
   tz Asia/Shanghai      - Set output timezone
   rule_tz UTC           - Set calculation timezone

🔧 Utilities:
   cache                 - Show cache statistics
   clear                 - Clear all caches
   benchmark             - Run performance benchmark
   
📖 Other:
   help                  - Show this help
   exit, quit, q         - Exit interactive mode
   
💡 Examples:
   > 2025-02-03T22:11:00
   > tz Asia/Hong_Kong
   > now
   > benchmark
"""
        print(self.colors.info(help_text))
    
    def parse_and_process_datetime(self, input_str: str, tz: str, rule_tz: str) -> None:
        """Parse datetime string and process it."""
        try:
            # Try various datetime formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%d %H:%M:%S%z'
            ]
            
            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(input_str, fmt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                # Try ISO format
                dt = datetime.fromisoformat(input_str)
            
            self.process_datetime(dt, tz, rule_tz)
            
        except Exception as e:
            print(self.colors.error(f"Invalid datetime format: {e}"))
            print(self.colors.info("Try formats like: 2025-02-03, 2025-02-03T22:11:00, or 'now'"))
    
    def process_datetime(self, dt: datetime, tz: str, rule_tz: str) -> None:
        """Process and display datetime information."""
        try:
            start_time = time.time()
            ts = TungShing(dt, tz=tz, rule_tz=rule_tz)
            calc_time = time.time() - start_time
            
            output = self.format_tungshing_output(ts, tz, rule_tz)
            print(output)
            print()
            print(self.colors.dim(f"⏱️  Calculation time: {calc_time:.3f}s"))
            print()
            
        except Exception as e:
            print(self.colors.error(f"Calculation failed: {e}"))
    
    def show_cache_stats(self) -> None:
        """Display cache statistics."""
        stats = get_cache_stats()
        
        print(self.colors.header("📊 Cache Statistics"))
        print(f"   Solar terms cached: {self.colors.colorize(str(stats['solar_terms']), Colors.CYAN)}")
        print(f"   Ganzhi cached: {self.colors.colorize(str(stats['ganzhi']), Colors.CYAN)}")
        print(f"   Lunar data cached: {self.colors.colorize(str(stats['lunar']), Colors.CYAN)}")
        print(f"   Instance cache: {self.colors.colorize(str(stats['instance_cache_size']), Colors.CYAN)}")
        print(f"   Total size: {self.colors.colorize(str(stats['total_size']), Colors.YELLOW)}/{self.colors.colorize(str(stats['max_size']), Colors.YELLOW)}")
        
        # Memory optimization suggestion
        if stats['total_size'] > stats['max_size'] * 0.7:
            print(self.colors.warning("💡 Consider running 'clear' to optimize memory"))
    
    def run_benchmark(self) -> None:
        """Run performance benchmark."""
        print(self.colors.header("🏃‍♂️ Performance Benchmark"))
        print(self.colors.info("Running calculations for various dates..."))
        
        # Test dates
        test_dates = [
            datetime(2025, 1, 1, 12, 0),
            datetime(2025, 2, 3, 22, 10, 13),  # Lichun
            datetime(2025, 6, 21, 10, 42),     # Summer solstice
            datetime(2025, 12, 22, 9, 21),     # Winter solstice
        ]
        
        timezones = ['Asia/Shanghai', 'Asia/Hong_Kong', 'UTC']
        
        total_calculations = len(test_dates) * len(timezones)
        calculations_done = 0
        
        # Warm-up
        print(self.colors.dim("Warming up cache..."))
        for dt in test_dates[:2]:
            TungShing(dt)
        
        # Clear cache for fair benchmark
        clear_all_caches()
        
        # Cold cache benchmark
        print(self.colors.info("Testing cold cache performance..."))
        cold_start = time.time()
        
        for dt in test_dates:
            for tz in timezones:
                ts = TungShing(dt, tz=tz, rule_tz=tz)
                # Access key properties to trigger calculations
                _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
                calculations_done += 1
        
        cold_time = time.time() - cold_start
        
        # Warm cache benchmark
        print(self.colors.info("Testing warm cache performance..."))
        warm_start = time.time()
        
        for dt in test_dates:
            for tz in timezones:
                ts = TungShing(dt, tz=tz, rule_tz=tz)
                _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
        
        warm_time = time.time() - warm_start
        
        # Results
        print()
        print(self.colors.header("📈 Benchmark Results"))
        print(f"   Total calculations: {self.colors.colorize(str(total_calculations), Colors.CYAN)}")
        print(f"   Cold cache time: {self.colors.colorize(f'{cold_time:.3f}s', Colors.YELLOW)} ({cold_time/total_calculations*1000:.1f}ms per calc)")
        print(f"   Warm cache time: {self.colors.colorize(f'{warm_time:.3f}s', Colors.GREEN)} ({warm_time/total_calculations*1000:.1f}ms per calc)")
        
        if warm_time > 0:
            speedup = cold_time / warm_time
            print(f"   Cache speedup: {self.colors.colorize(f'{speedup:.1f}x', Colors.MAGENTA + Colors.BOLD)}")
        
        # Memory usage
        stats = get_cache_stats()
        print(f"   Cache entries: {self.colors.colorize(str(stats['total_size']), Colors.CYAN)}")
    
    def export_data(self, ts: TungShing, format: str = 'json') -> str:
        """Export TungShing data in various formats."""
        data = {
            'timestamp': ts.date.isoformat(),
            'four_pillars': {
                'year': ts.year8Char,
                'month': ts.month8Char,
                'day': ts.day8Char,
                'hour': ts.twohour8Char
            },
            'lunar_calendar': {
                'year': ts.lunarYear,
                'month': ts.lunarMonth,
                'day': ts.lunarDay,
                'year_cn': ts.lunarYearCn,
                'month_cn': ts.lunarMonthCn,
                'day_cn': ts.lunarDayCn
            }
        }
        
        # Add solar term if available
        if hasattr(ts, 'termTodayExact_ruleTz') and ts.termTodayExact_ruleTz:
            data['solar_term'] = {
                'rule_tz': ts.termTodayExact_ruleTz,
                'cn8': getattr(ts, 'termTodayExact_cn8', None)
            }
        
        if format.lower() == 'json':
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)


def create_parser() -> argparse.ArgumentParser:
    """Create comprehensive argument parser."""
    parser = argparse.ArgumentParser(
        prog="tungshing",
        description=(
            "TungShing CLI - 严格口径的黄历/通胜\n"
            "Advanced Chinese lunar calendar with GB/T 33661-2017 compliance"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tungshing                                      # Current time, interactive mode
  tungshing --datetime 2025-02-03T22:11:00+08:00
  tungshing --datetime 2025-02-03T22:11:00 --tz Asia/Shanghai
  tungshing --interactive                        # Start interactive mode
  tungshing --benchmark                          # Run performance benchmark
  tungshing --cache-stats                        # Show cache statistics

For more information: https://github.com/xianyu564/tungshing
        """
    )
    
    # Main arguments
    parser.add_argument(
        "--datetime", "--dt",
        dest="dt",
        metavar="DATETIME",
        help=(
            "ISO datetime string (e.g., 2025-02-03T22:11:00+08:00)\n"
            "If timezone not specified, uses --tz value"
        )
    )
    
    parser.add_argument(
        "--tz",
        dest="tz",
        default="Asia/Shanghai",
        metavar="TIMEZONE",
        help="Output/local timezone (default: Asia/Shanghai)"
    )
    
    parser.add_argument(
        "--rule-tz",
        dest="rule_tz",
        default="Asia/Shanghai",
        metavar="TIMEZONE",
        help="Boundary calculation timezone (default: Asia/Shanghai)"
    )
    
    # Interactive and utility modes
    parser.add_argument(
        "--interactive", "--i",
        action="store_true",
        help="Start interactive exploration mode"
    )
    
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run performance benchmark"
    )
    
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache statistics"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all caches"
    )
    
    # Output options
    parser.add_argument(
        "--export",
        choices=["json"],
        help="Export data in specified format"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}"
    )
    
    return parser


def main() -> None:
    """Enhanced main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Initialize CLI
    cli = TungShingCLI()
    
    # Disable colors if requested
    if args.no_color:
        Colors.colorize = lambda text, color: text
    
    try:
        # Handle utility commands
        if args.cache_stats:
            cli.show_cache_stats()
            return
        
        if args.clear_cache:
            clear_all_caches()
            print(cli.colors.success("All caches cleared"))
            return
        
        if args.benchmark:
            cli.run_benchmark()
            return
        
        if args.interactive or (not args.dt and not sys.argv[1:]):
            cli.interactive_mode()
            return
        
        # Parse datetime
        if args.dt:
            try:
                dt = datetime.fromisoformat(args.dt)
            except ValueError as e:
                parser.error(f"Invalid --datetime format: {e}\nUse ISO 8601 format like: 2025-02-03T22:11:00+08:00")
        else:
            dt = datetime.now(ZoneInfo(args.tz))
        
        # Create TungShing object and display results
        ts = TungShing(dt, tz=args.tz, rule_tz=args.rule_tz)
        
        if args.export:
            # Export mode
            output = cli.export_data(ts, args.export)
            print(output)
        else:
            # Standard formatted output
            output = cli.format_tungshing_output(ts, args.tz, args.rule_tz)
            print(output)
        
    except TungShingError as e:
        print(cli.colors.error(str(e)), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n" + cli.colors.info("Interrupted"))
        sys.exit(1)
    except Exception as e:
        print(cli.colors.error(f"Unexpected error: {e}"), file=sys.stderr)
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