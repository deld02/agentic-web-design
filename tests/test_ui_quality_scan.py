from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from ui_quality_scan import scan_implementation  # noqa: E402


class UIQualityScanTests(unittest.TestCase):
    def test_critical_accessibility_and_placeholder_defects_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "index.html").write_text(
                '<style>button{outline:none;transition:all .2s}</style><img src="x.png"><p>Lorem ipsum</p>',
                encoding="utf-8",
            )
            report = scan_implementation(root)
            rules = {item["rule"] for item in report["findings"]}
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue({"FOCUS_REMOVED", "IMG_ALT", "PLACEHOLDER_CONTENT"}.issubset(rules))

    def test_generic_signals_are_advisory_not_beauty_failures(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "style.css").write_text('.card{transition:all .2s;animation:pop 1s bounce}', encoding="utf-8")
            report = scan_implementation(root)
            self.assertEqual(report["status"], "PASS")
            self.assertTrue(all(item["severity"] == "ADVISORY" for item in report["findings"]))


if __name__ == "__main__":
    unittest.main()
