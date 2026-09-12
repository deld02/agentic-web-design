"""Owner evidence must be checked before handing work to the next stage."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import project_validation as validation


class DirectionExitTests(unittest.TestCase):
    def test_divergence_requires_boards_without_premature_reviewer_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / "creative-direction.md").write_text("# Direction\n", encoding="utf-8")
            owner_errors = validation.direction_divergence_errors(project, require_selection=False)
            self.assertTrue(any("three divergent" in error for error in owner_errors))
            self.assertFalse(any("selection" in error or "selected direction" in error for error in owner_errors))
            gate_errors = validation.direction_divergence_errors(project)
            self.assertTrue(any("selected direction" in error for error in gate_errors))

    def test_three_boards_suffice_before_reviewer_selection(self):
        rows = [[f"DIR-{index:03}", *[f"dimension-{column}-{index}" for column in range(6)],
                 f"evidence/board-{index}.png"] for index in range(1, 4)]
        with patch.object(validation, "markdown", return_value=""), \
             patch.object(validation, "table_rows", return_value=rows), \
             patch.object(validation, "_physical_composition_error", return_value=None):
            # Physical-file checking is tested elsewhere; this test isolates the
            # owner/reviewer boundary rather than claiming visual quality.
            self.assertEqual(validation.direction_divergence_errors(ROOT, require_selection=False), [])
            self.assertTrue(validation.direction_divergence_errors(ROOT))


if __name__ == "__main__":
    unittest.main()
