import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validation_user_authority import record_master_confirmation


class MasterConfirmationBoundaryTests(unittest.TestCase):
    def test_empty_signal_does_not_consume_following_heading(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "creative-direction.md"
            tail = "## Creative master handoff\nCREATIVE_MASTER: AM-001\n"
            path.write_text("## Artistic master confirmation\nSTATUS: PENDING\nUSER_SIGNAL:\n\n" + tail, encoding="utf-8")
            record_master_confirmation(path, "DELEGATED", r"Delego \1 la decisión")
            updated = path.read_text(encoding="utf-8")
            self.assertTrue(updated.endswith(tail))
            self.assertIn(r"USER_SIGNAL: Delego \1 la decisión", updated)

    def test_missing_field_cannot_change_later_section(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "creative-direction.md"
            original = "## Artistic master confirmation\nSTATUS: PENDING\n\n## Other\nUSER_SIGNAL: unrelated\n"
            path.write_text(original, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing USER_SIGNAL"):
                record_master_confirmation(path, "APPROVED", "Sí")
            self.assertEqual(path.read_text(encoding="utf-8"), original)
