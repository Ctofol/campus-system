import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pose_analyzer import analyzer


class PoseAnalyzerDetailTests(unittest.TestCase):
    def test_missing_video_returns_reviewable_detail(self):
        count, qualified, score, detail = analyzer.analyze_test_video(
            "/uploads/not-exists.mp4",
            "push_up",
        )
        data = json.loads(detail)

        self.assertEqual(count, 0)
        self.assertFalse(qualified)
        self.assertEqual(score, 0)
        self.assertEqual(data["review_reason"], "video_not_found_local")
        self.assertIn("video_not_found_local", data["risk_flags"])

    def test_success_detail_contains_quality_and_confidence(self):
        raw = {
            "engine": "mediapipe",
            "count": 12,
            "valid_reps": 12,
            "invalid_reps": 1,
            "partial_reps": 2,
            "frames_sampled": 120,
            "pose_frames": 112,
            "valid_pose_frames": 100,
            "confidence": 0.88,
            "quality": {"avg_visibility": 0.91, "avg_body_area": 0.22},
            "review_reason": None,
            "risk_flags": [],
        }

        with patch.object(analyzer, "_resolve_video_path", return_value="fake.mp4"), patch.object(
            analyzer, "_analyze_with_mediapipe", return_value=raw
        ):
            count, qualified, score, detail = analyzer.analyze_test_video("fake.mp4", "sit_up", 10)

        data = json.loads(detail)
        self.assertEqual(count, 12)
        self.assertTrue(qualified)
        self.assertGreaterEqual(score, 60)
        self.assertEqual(data["confidence"], 0.88)
        self.assertEqual(data["valid_reps"], 12)
        self.assertEqual(data["quality"]["avg_visibility"], 0.91)

    def test_review_reason_blocks_qualification(self):
        raw = {
            "engine": "mediapipe",
            "count": 20,
            "confidence": 0.9,
            "review_reason": "pose_quality_too_low",
            "risk_flags": ["pose_quality_too_low"],
        }

        with patch.object(analyzer, "_resolve_video_path", return_value="fake.mp4"), patch.object(
            analyzer, "_analyze_with_mediapipe", return_value=raw
        ):
            count, qualified, score, detail = analyzer.analyze_test_video("fake.mp4", "pull_up", 10)

        data = json.loads(detail)
        self.assertEqual(count, 20)
        self.assertFalse(qualified)
        self.assertGreater(score, 0)
        self.assertEqual(data["review_reason"], "pose_quality_too_low")


if __name__ == "__main__":
    unittest.main()
