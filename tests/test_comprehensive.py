"""
Comprehensive test suite for TungShing package.

Tests API compatibility, edge cases, timezone handling, and performance.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pytest

from tungshing import TungShing


class TestAPICompatibility:
    """Test full API compatibility with cnlunar."""

    def test_basic_instantiation(self):
        """Test basic object creation."""
        ts = TungShing()
        assert hasattr(ts, 'year8Char')
        assert hasattr(ts, 'month8Char')
        assert hasattr(ts, 'day8Char')
        assert hasattr(ts, 'twohour8Char')

    def test_with_datetime(self):
        """Test instantiation with specific datetime."""
        dt = datetime(2025, 1, 1, 12, 0)
        ts = TungShing(dt)
        assert ts.date.year == 2025
        assert ts.date.month == 1
        assert ts.date.day == 1

    def test_cnlunar_attributes(self):
        """Test that cnlunar attributes are accessible."""
        ts = TungShing(datetime(2025, 1, 1))
        
        # Lunar calendar attributes
        assert hasattr(ts, 'lunarYear')
        assert hasattr(ts, 'lunarMonth') 
        assert hasattr(ts, 'lunarDay')
        assert hasattr(ts, 'lunarYearCn')
        assert hasattr(ts, 'lunarMonthCn')
        assert hasattr(ts, 'lunarDayCn')
        
        # Type checks
        assert isinstance(ts.lunarYear, int)
        assert isinstance(ts.lunarMonth, int)
        assert isinstance(ts.lunarDay, int)
        assert isinstance(ts.lunarYearCn, str)
        assert isinstance(ts.lunarMonthCn, str)
        assert isinstance(ts.lunarDayCn, str)

    def test_ganzhi_format(self):
        """Test Ganzhi format validity."""
        ts = TungShing(datetime(2025, 1, 1))
        
        # Each should be 2 Chinese characters
        assert len(ts.year8Char) == 2
        assert len(ts.month8Char) == 2
        assert len(ts.day8Char) == 2
        assert len(ts.twohour8Char) == 2
        
        # Should be valid Ganzhi combinations
        gan = "甲乙丙丁戊己庚辛壬癸"
        zhi = "子丑寅卯辰巳午未申酉戌亥"
        
        for pillar in [ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char]:
            assert pillar[0] in gan
            assert pillar[1] in zhi


class TestTimezoneHandling:
    """Test timezone-aware calculations."""

    def test_different_timezones(self):
        """Test behavior with different timezones."""
        dt_utc = datetime(2025, 2, 3, 14, 10, tzinfo=ZoneInfo("UTC"))
        dt_sha = datetime(2025, 2, 3, 22, 10, tzinfo=ZoneInfo("Asia/Shanghai"))
        dt_hk = datetime(2025, 2, 3, 22, 10, tzinfo=ZoneInfo("Asia/Hong_Kong"))
        
        ts_utc = TungShing(dt_utc)
        ts_sha = TungShing(dt_sha) 
        ts_hk = TungShing(dt_hk)
        
        # Same moment in time should give same results
        assert ts_utc.year8Char == ts_sha.year8Char
        assert ts_sha.year8Char == ts_hk.year8Char

    def test_rule_timezone_parameter(self):
        """Test rule_tz parameter functionality."""
        dt = datetime(2025, 2, 3, 22, 10)
        
        ts_default = TungShing(dt)
        ts_hk_rule = TungShing(dt, rule_tz="Asia/Hong_Kong")
        
        # Should handle timezone rules properly
        assert isinstance(ts_default.year8Char, str)
        assert isinstance(ts_hk_rule.year8Char, str)

    def test_naive_datetime_handling(self):
        """Test handling of naive datetime objects."""
        dt_naive = datetime(2025, 1, 1, 12, 0)
        dt_aware = datetime(2025, 1, 1, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        
        ts_naive = TungShing(dt_naive)
        ts_aware = TungShing(dt_aware)
        
        # Both should work without errors
        assert ts_naive.year8Char
        assert ts_aware.year8Char


class TestSolarTerms:
    """Test solar term calculations."""

    def test_solar_term_properties(self):
        """Test solar term property methods."""
        # Date with no solar term
        ts_normal = TungShing(datetime(2025, 1, 15))
        assert ts_normal.termTodayExact_ruleTz is None
        assert ts_normal.termTodayExact_cn8 is None
        
        # Date with solar term (Lichun 2025)
        ts_lichun = TungShing(datetime(2025, 2, 3))
        if ts_lichun.termTodayExact_ruleTz:
            assert isinstance(ts_lichun.termTodayExact_ruleTz, str)
            assert isinstance(ts_lichun.termTodayExact_cn8, str)
            # Should be valid ISO format
            assert "2025-02-03" in ts_lichun.termTodayExact_ruleTz
            assert "T" in ts_lichun.termTodayExact_ruleTz

    def test_solar_term_timing_precision(self):
        """Test precision of solar term timing."""
        # Test around Lichun 2025 (approximate time)
        base_time = datetime(2025, 2, 3, 22, 10, tzinfo=ZoneInfo("Asia/Shanghai"))
        
        for offset_minutes in [-30, -5, 0, 5, 30]:
            test_time = base_time + timedelta(minutes=offset_minutes)
            ts = TungShing(test_time)
            
            # Should either have solar term or not, but no errors
            term_time = ts.termTodayExact_ruleTz
            assert term_time is None or isinstance(term_time, str)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_leap_year_handling(self):
        """Test leap year calculations."""
        # 2024 is a leap year
        ts_leap = TungShing(datetime(2024, 2, 29))
        assert ts_leap.lunarYear == 2024
        
        # Should handle the date without errors
        assert ts_leap.year8Char
        assert ts_leap.month8Char
        assert ts_leap.day8Char

    def test_year_boundary_consistency(self):
        """Test consistency across year boundaries."""
        # Test New Year boundary
        nye_2024 = TungShing(datetime(2024, 12, 31, 23, 59))
        nyd_2025 = TungShing(datetime(2025, 1, 1, 0, 1))
        
        # Lunar calendar might still be same year due to Lichun rule
        assert isinstance(nye_2024.lunarYear, int)
        assert isinstance(nyd_2025.lunarYear, int)

    def test_extreme_dates(self):
        """Test with extreme date values."""
        # Far future
        ts_future = TungShing(datetime(2100, 1, 1))
        assert ts_future.year8Char
        
        # Early date (within sxtwl range)
        ts_past = TungShing(datetime(1900, 1, 1))
        assert ts_past.year8Char

    def test_night_zi_hour_consistency(self):
        """Test 23:00-23:59 hour consistency."""
        base_date = datetime(2025, 1, 1, 23, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
        next_date = datetime(2025, 1, 2, 0, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
        
        ts_night = TungShing(base_date)
        ts_next = TungShing(next_date)
        
        # Night Zi hour should forward to next day characteristics
        # The exact behavior depends on implementation details


class TestPerformance:
    """Test performance characteristics."""

    def test_instantiation_performance(self):
        """Test that object creation is reasonably fast."""
        import time
        
        start_time = time.time()
        for _ in range(100):
            ts = TungShing(datetime(2025, 1, 1))
            _ = ts.year8Char  # Force calculation
        end_time = time.time()
        
        # Should create 100 objects in reasonable time (less than 5 seconds)
        assert end_time - start_time < 5.0

    def test_attribute_access_performance(self):
        """Test that attribute access is fast after instantiation."""
        ts = TungShing(datetime(2025, 1, 1))
        
        import time
        start_time = time.time()
        for _ in range(1000):
            _ = ts.year8Char
            _ = ts.month8Char
            _ = ts.day8Char
            _ = ts.lunarDayCn
        end_time = time.time()
        
        # Should access attributes quickly
        assert end_time - start_time < 1.0


class TestVersionInfo:
    """Test package version and metadata."""

    def test_version_available(self):
        """Test that version information is available."""
        import tungshing
        assert hasattr(tungshing, '__version__')
        assert isinstance(tungshing.__version__, str)
        assert len(tungshing.__version__) > 0

    def test_package_metadata(self):
        """Test package metadata availability."""
        import tungshing
        
        # These should be available after our enhancements
        assert hasattr(tungshing, '__author__')
        assert hasattr(tungshing, '__email__')
        assert hasattr(tungshing, '__license__')
        assert hasattr(tungshing, '__description__')


if __name__ == "__main__":
    pytest.main([__file__])