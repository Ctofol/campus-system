import unittest
from types import SimpleNamespace

from app.services.face_verify_service import verify_run_faces


class FaceVerifyTests(unittest.TestCase):
    def test_missing_both_photos(self):
        outcome = verify_run_faces([])
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.fail_code, "MISSING_PHOTO")

    def test_has_start_and_end_fallback(self):
        evidence = [
            SimpleNamespace(evidence_type="start_face", data_ref="/uploads/202601/a.jpg"),
            SimpleNamespace(evidence_type="end_face", data_ref="/uploads/202601/b.jpg"),
        ]
        outcome = verify_run_faces(evidence)
        self.assertTrue(outcome.ok)
        self.assertTrue(outcome.face_verified)


if __name__ == "__main__":
    unittest.main()
