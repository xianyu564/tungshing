from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from tungshing import TungShing


TAIPEI = ZoneInfo("Asia/Shanghai")


def _same_forward_fields(a, b):
    keys = [
        "lunarYear","lunarMonth","lunarDay",
        "lunarYearCn","lunarMonthCn","lunarDayCn",
        "day8Char","twohour8Char",
    ]
    for k in keys:
        if hasattr(a, k) and hasattr(b, k):
            va, vb = getattr(a, k), getattr(b, k)
            assert va == vb


def test_lichun_2024_switch_year():
    t_before = datetime(2024, 2, 4, 16, 26, 30, tzinfo=TAIPEI)
    t_after = datetime(2024, 2, 4, 16, 27, 30, tzinfo=TAIPEI)
    a = TungShing(t_before)
    b = TungShing(t_after)
    assert a.year8Char != b.year8Char


def test_lichun_2025_switch_year():
    t_before = datetime(2025, 2, 3, 22, 9, 50, tzinfo=TAIPEI)
    t_after = datetime(2025, 2, 3, 22, 10, 30, tzinfo=TAIPEI)
    c = TungShing(t_before)
    d = TungShing(t_after)
    assert c.year8Char != d.year8Char


def test_jingzhe_switch_month():
    jz_pre = TungShing(datetime(2025, 3, 5, 16, 6, 30, tzinfo=TAIPEI))
    jz_post = TungShing(datetime(2025, 3, 5, 16, 7, 30, tzinfo=TAIPEI))
    assert jz_pre.month8Char != jz_post.month8Char


def test_autumnal_equinox_not_switch_month():
    qf_pre = TungShing(datetime(2025, 9, 23, 2, 18, 30, tzinfo=TAIPEI))
    qf_post = TungShing(datetime(2025, 9, 23, 2, 20, 0, tzinfo=TAIPEI))
    assert qf_pre.month8Char == qf_post.month8Char


def test_23_to_nextday_forward_block():
    def check_2300_block(y, m, d):
        e = TungShing(datetime(y, m, d, 23, 30, tzinfo=TAIPEI))
        f = TungShing(datetime(y, m, d, 0, 30, tzinfo=TAIPEI) + timedelta(days=1))
        _same_forward_fields(e, f)
        p2259 = TungShing(datetime(y, m, d, 22, 59, tzinfo=TAIPEI))
        p2300 = TungShing(datetime(y, m, d, 23, 0, tzinfo=TAIPEI))
        _same_forward_fields(p2300, f)
        changed = (
            (p2259.lunarDay, p2259.lunarDayCn, p2259.day8Char)
            != (p2300.lunarDay, p2300.lunarDayCn, p2300.day8Char)
        )
        assert changed

    check_2300_block(2025, 1, 20)
    check_2300_block(2025, 2, 18)
    check_2300_block(2025, 9, 23)
    check_2300_block(2025, 12, 21)
    check_2300_block(2025, 8, 7)


