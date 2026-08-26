import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from code_quality import quality_errors  # noqa: E402


class ArchitectureTests(unittest.TestCase):
    def test_source_organization_ratchets(self):
        self.assertEqual([], quality_errors())


if __name__ == "__main__":
    unittest.main()
