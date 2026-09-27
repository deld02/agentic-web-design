"""Local opt-in and credential handling; no framework downloads."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import harness_local_build as local
import harness_frontend_build as build


class LocalBuildTests(unittest.TestCase):
    def test_unapproved_cannot_execute(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(local.subprocess, "Popen") as run:
            with self.assertRaisesRegex(ValueError, "operator approval"):
                local.run_local(Path("unused"), "a" * 64)
            run.assert_not_called()

    def test_environment_and_direct_node_invocation(self):
        with tempfile.TemporaryDirectory() as folder:
            capability = {"available": True, "node": str(Path(folder) / "node.exe"), "npm_cli": "npm-cli.js"}
            with patch.dict(os.environ, {"AGENTIC_LOCAL_APPROVED_SHA256": "abc", "OPENAI_API_KEY": "secret"}), \
                 patch.object(local, "local_capability", return_value=capability), \
                 patch.object(local.subprocess, "Popen") as run:
                run.return_value.wait.return_value = 0
                local.run_local(Path(folder), "abc")
            self.assertEqual(2, run.call_count)
            self.assertNotIn("OPENAI_API_KEY", run.call_args.kwargs["env"])
            self.assertNotIn("shell", run.call_args.kwargs)
            self.assertEqual(["--ignore-scripts", "run", "build"], run.call_args.args[0][2:])

    def test_unknown_backend_fails_closed(self):
        with patch.dict(os.environ, {"AGENTIC_BUILD_BACKEND": "unknown"}):
            self.assertFalse(build.build_capability()["available"])
