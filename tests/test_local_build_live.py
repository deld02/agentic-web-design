"""Opt-in real npm/Vite export. Downloads dependencies; never runs in default suite."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from contextlib import nullcontext
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from harness_frontend_build import build_export, implementation_digest
from harness_local_build import local_capability


@unittest.skipUnless(os.getenv("AGENTIC_RUN_LOCAL_BUILD_TESTS") == "1", "explicit live npm opt-in required")
class LocalBuildLiveTest(unittest.TestCase):
    def test_vite_export(self):
        # Preserve real npm work for diagnosis; Windows package cache cleanup can
        # race with background file scanners. No recursive deletion here.
        with nullcontext(tempfile.mkdtemp(prefix="awd-vite-")) as directory:
            project = Path(directory) / "project"
            source = project / "frontend"
            source.mkdir(parents=True)
            package = {"name": "awd-local-smoke", "version": "1.0.0", "private": True,
                       "scripts": {"build": "vite build"}, "devDependencies": {"vite": "7.1.7"}}
            (source / "package.json").write_text(json.dumps(package))
            (source / "runtime.json").write_text('{"target":"static","external_services":[]}')
            (source / "index.html").write_text('<!doctype html><html><body><h1>Local build</h1><script type="module" src="/main.js"></script></body></html>')
            (source / "main.js").write_text('document.body.dataset.ready = "yes";')
            capability = local_capability()
            result = subprocess.run([capability["node"], capability["npm_cli"], "install", "--package-lock-only",
                                     "--ignore-scripts", "--no-audit", "--no-fund"], cwd=source,
                                    capture_output=True, timeout=120)
            self.assertEqual(0, result.returncode, "lockfile preparation failed")
            with patch.dict(os.environ, {"AGENTIC_LOCAL_APPROVED_SHA256": implementation_digest(source)}):
                record = build_export(project, "dist")
            self.assertEqual("local", record["backend"])
            self.assertFalse(record["isolated"])
            self.assertTrue((project / "implementation/index.html").is_file())
            self.assertTrue(list((project / "implementation/assets").glob("*.js")))
