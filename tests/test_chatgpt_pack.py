from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_chatgpt_pack import FORBIDDEN, build_pack  # noqa: E402


class ChatGPTPackTests(unittest.TestCase):
    def test_pack_contains_current_runtime_without_historical_audits(self):
        with tempfile.TemporaryDirectory() as directory:
            pack, archive = build_pack(Path(directory) / "new-output")
            self.assertTrue((pack / "START-HERE.md").is_file())
            self.assertTrue((pack / "tools" / "evaluation_harness.py").is_file())
            self.assertFalse((pack / "docs" / "audit").exists())
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(archive) as bundle:
                self.assertTrue(any(name.endswith("START-HERE.md") for name in bundle.namelist()))

    def test_pack_has_current_version_and_no_legacy_architecture_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            pack, _archive = build_pack(Path(directory))
            runtime = json.loads((pack / "runtime-manifest.json").read_text(encoding="utf-8"))
            current = json.loads((ROOT / "repo-manifest.json").read_text(encoding="utf-8"))["version"]
            self.assertEqual(runtime["system_version"], current)
            corpus = "\n".join(
                path.read_text(encoding="utf-8", errors="ignore")
                for path in pack.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}
            ).lower()
            for token in FORBIDDEN:
                self.assertNotIn(token.lower(), corpus)

    def test_pack_validates_as_a_standalone_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            pack, _archive = build_pack(Path(directory))
            result = subprocess.run(
                [sys.executable, "tools/validate_system.py"],
                cwd=pack,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
