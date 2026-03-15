import unittest
from unittest.mock import patch
from types import SimpleNamespace

from app.services.score_service import verify_activity, calculate_total_score


class FakeQuery:
    """Simple fake SQLAlchemy query object used for counting valid activities."""

    def __init__(self, count_result: int):
        self._count_result = count_result

    def filter(self, *args, **kwargs):
        # In tests we don't need to actually apply filters
        return self

    def count(self) -> int:
        return self._count_result


class FakeDB:
    """Fake DB session that always returns a query with a fixed count result."""

    def __init__(self, count_result: int = 0):
        self._count_result = count_result

    def query(self, *args, **kwargs):
        return FakeQuery(self._count_result)


def make_activity(distance_km: float, pace_min_per_km: float):
    """Helper to construct a minimal activity object accepted by verify_activity."""
    metrics = SimpleNamespace(
        distance=distance_km,
        duration=0,
        pace=str(pace_min_per_km),
    )
    # Two face evidences to satisfy face check when needed
    evidence = [
        SimpleNamespace(evidence_type="start_face", data_ref="start.jpg"),
        SimpleNamespace(evidence_type="end_face", data_ref="end.jpg"),
    ]
    activity = SimpleNamespace(
        metrics=metrics,
        evidence=evidence,
        started_at=None,
    )
    return activity


class SunshineRunLogicTests(unittest.TestCase):
    """自动化测试：阳光跑审核逻辑与阶梯计分算法。"""

    # 场景 A：性别与里程标准校验

    @patch("app.services.score_service.random.random", return_value=0.5)
    def test_male_distance_below_standard_is_invalid(self, _mock_random):
        user = SimpleNamespace(id=1, gender="male")
        activity = make_activity(distance_km=1.9, pace_min_per_km=5.0)
        db = FakeDB(count_result=0)

        is_valid, reason, face_verified = verify_activity(user, activity, db)

        self.assertFalse(is_valid)
        self.assertEqual(reason, "里程不足")
        self.assertFalse(face_verified)

    @patch("app.services.score_service.random.random", return_value=0.5)
    def test_male_distance_meet_standard_is_valid(self, _mock_random):
        user = SimpleNamespace(id=1, gender="male")
        activity = make_activity(distance_km=2.1, pace_min_per_km=5.0)
        db = FakeDB(count_result=0)

        is_valid, reason, face_verified = verify_activity(user, activity, db)

        self.assertTrue(is_valid)
        self.assertEqual(reason, "")
        self.assertTrue(face_verified)

    @patch("app.services.score_service.random.random", return_value=0.5)
    def test_female_distance_below_standard_is_invalid(self, _mock_random):
        user = SimpleNamespace(id=2, gender="female")
        activity = make_activity(distance_km=1.1, pace_min_per_km=5.0)
        db = FakeDB(count_result=0)

        is_valid, reason, face_verified = verify_activity(user, activity, db)

        self.assertFalse(is_valid)
        self.assertEqual(reason, "里程不足")
        self.assertFalse(face_verified)

    @patch("app.services.score_service.random.random", return_value=0.5)
    def test_female_distance_meet_standard_is_valid(self, _mock_random):
        user = SimpleNamespace(id=2, gender="female")
        activity = make_activity(distance_km=1.3, pace_min_per_km=5.0)
        db = FakeDB(count_result=0)

        is_valid, reason, face_verified = verify_activity(user, activity, db)

        self.assertTrue(is_valid)
        self.assertEqual(reason, "")
        self.assertTrue(face_verified)

    # 场景 B：配速区间校验

    @patch("app.services.score_service.random.random", return_value=0.5)
    def test_pace_too_fast_is_invalid(self, _mock_random):
        # 2.0km, 5 分钟 => 2.5 min/km，低于 3
        user = SimpleNamespace(id=3, gender="male")
        activity = make_activity(distance_km=2.0, pace_min_per_km=2.5)
        db = FakeDB(count_result=0)

        is_valid, reason, face_verified = verify_activity(user, activity, db)

        self.assertFalse(is_valid)
        self.assertEqual(reason, "配速异常")
        self.assertFalse(face_verified)

    @patch("app.services.score_service.random.random", return_value=0.5)
    def test_pace_too_slow_is_invalid(self, _mock_random):
        # 2.0km, 25 分钟 => 12.5 min/km，高于 10
        user = SimpleNamespace(id=3, gender="male")
        activity = make_activity(distance_km=2.0, pace_min_per_km=12.5)
        db = FakeDB(count_result=0)

        is_valid, reason, face_verified = verify_activity(user, activity, db)

        self.assertFalse(is_valid)
        self.assertEqual(reason, "配速异常")
        self.assertFalse(face_verified)

    @patch("app.services.score_service.random.random", return_value=0.5)
    def test_pace_in_valid_range_is_valid(self, _mock_random):
        # 2.0km, 10 分钟 => 5.0 min/km，在 3-10 范围内
        user = SimpleNamespace(id=3, gender="male")
        activity = make_activity(distance_km=2.0, pace_min_per_km=5.0)
        db = FakeDB(count_result=0)

        is_valid, reason, face_verified = verify_activity(user, activity, db)

        self.assertTrue(is_valid)
        self.assertEqual(reason, "")
        self.assertTrue(face_verified)

    # 场景 C：阶梯计分算法校验

    def test_score_ladder_algorithm(self):
        # 0-10 次：0 分
        self.assertEqual(calculate_total_score(10), 0)
        # 11 次：42 分
        self.assertEqual(calculate_total_score(11), 42)
        # 19 次：58 分 (42 + 8*2)
        self.assertEqual(calculate_total_score(19), 58)
        # 20 次：60 分（及格线）
        self.assertEqual(calculate_total_score(20), 60)
        # 40 次：100 分（满分）
        self.assertEqual(calculate_total_score(40), 100)
        # >40 次：封顶 100 分
        self.assertEqual(calculate_total_score(45), 100)

    # 场景 D：单日限次校验

    @patch("app.services.score_service.random.random", return_value=0.5)
    def test_daily_limit_only_first_valid(self, _mock_random):
        user = SimpleNamespace(id=4, gender="male")
        activity1 = make_activity(distance_km=2.1, pace_min_per_km=5.0)
        activity2 = make_activity(distance_km=2.1, pace_min_per_km=5.0)

        # 第一次：当日尚无达标记录 => 允许达标
        db_first = FakeDB(count_result=0)
        is_valid1, reason1, face_verified1 = verify_activity(user, activity1, db_first)

        # 第二次：模拟当日已有 1 条达标记录 => 触发“今日已达标”
        db_second = FakeDB(count_result=1)
        is_valid2, reason2, face_verified2 = verify_activity(user, activity2, db_second)

        self.assertTrue(is_valid1)
        self.assertEqual(reason1, "")
        self.assertTrue(face_verified1)

        self.assertFalse(is_valid2)
        self.assertIn("今日已达标", reason2)
        self.assertFalse(face_verified2)


if __name__ == "__main__":
    # 允许直接 python 运行该文件时输出详细测试报告
    unittest.main(verbosity=2)

