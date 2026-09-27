"""Safety and lifecycle tests. Docker commands are mocked, not live framework proof."""
import json
import io
import tarfile
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import harness_frontend_build as build


class FrontendBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name).resolve() / "project"
        self.source = self.project / "frontend"
        self.source.mkdir(parents=True)
        for name, value in {"package.json":{"scripts":{"build":"test"}},
                            "package-lock.json":{"lockfileVersion":3,"packages":{}},
                            "runtime.json":{"target":"static","external_services":[]}}.items():
            (self.source / name).write_text(json.dumps(value))

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_runtime_does_not_write(self):
        with patch.object(build, "build_capability", return_value={"available":False}):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                build.build_export(self.project, "out")
        self.assertFalse((self.project / "evidence").exists())

    def test_reject_external_service_and_old_output(self):
        (self.source / "runtime.json").write_text('{"target":"static","external_services":["database"]}')
        with self.assertRaisesRegex(ValueError, "external services"):
            build.validate_source(self.source)
        (self.source / "runtime.json").write_text('{"target":"static","external_services":[]}')
        (self.source / "out").mkdir()
        with self.assertRaisesRegex(ValueError, "previous build"):
            build.validate_source(self.source)

    def test_lock_and_secret_rejected(self):
        (self.source / "package-lock.json").write_text('{"lockfileVersion":3,"packages":{"x":{"resolved":"file:../x"}}}')
        with self.assertRaisesRegex(ValueError, "public npm"):
            build.validate_source(self.source)
        (self.source / ".env").write_text("not-a-secret")
        with self.assertRaisesRegex(ValueError, "secrets"):
            build.checked_files(self.source)

    def test_container_limits_no_host_write(self):
        with patch.object(build.shutil, "which", return_value="docker"):
            cmd = build.container_command("node@sha256:" + "a"*64, "awd-test", self.source, ["sleep","600"], "bridge")
        self.assertIn("--read-only",cmd)
        self.assertIn("--cap-drop=ALL",cmd)
        self.assertIn("--pids-limit=128",cmd)
        self.assertTrue(any("target=/source,readonly" in item for item in cmd))
        self.assertFalse(any("OPENAI" in item for item in cmd))

    def test_failure_preserves_implementation_and_stops_container(self):
        destination = self.project / "implementation"
        destination.mkdir()
        (destination / "index.html").write_text("original")
        with patch.object(build, "build_capability", return_value={"available":True}), \
             patch.dict(build.os.environ, {"AGENTIC_BUILD_IMAGE":"test"}), \
             patch.object(build.shutil,"which",return_value="docker"), \
             patch.object(build,"run_container",side_effect=RuntimeError("failed")), \
             patch.object(build.subprocess,"run") as cleanup:
            cleanup.return_value.returncode = 0
            with self.assertRaisesRegex(RuntimeError,"failed"):
                build.build_export(self.project,"out")
        self.assertEqual("original",(destination / "index.html").read_text())
        self.assertEqual(["docker","rm","--force"],cleanup.call_args.args[0][:3])

    def test_changed_source_requires_rebuild(self):
        evidence = self.project / "evidence"
        evidence.mkdir()
        (evidence / "frontend-build.json").write_text(json.dumps({"source_sha256":build.implementation_digest(self.source)}))
        self.assertEqual([],build.build_freshness_errors(self.project))
        (self.source / "app.js").write_text("changed")
        self.assertTrue(build.build_freshness_errors(self.project))

    def test_success_build_disconnects_network_and_preserves_old_export(self):
        old = self.project / "implementation"
        old.mkdir()
        (old / "index.html").write_text("original")
        def export(_docker, _name, _output, destination):
            (destination / "index.html").write_text("new export")
        with patch.object(build, "build_capability", return_value={"available":True}), \
             patch.dict(build.os.environ, {"AGENTIC_BUILD_IMAGE":"test"}), \
             patch.object(build.shutil,"which",return_value="docker"), \
             patch.object(build,"run_container") as commands, \
             patch.object(build,"copy_export",side_effect=export), \
             patch.object(build.subprocess,"run") as cleanup:
            cleanup.return_value.returncode = 0
            record = build.build_export(self.project,"out")
        self.assertEqual("new export",(old / "index.html").read_text())
        self.assertEqual("original",(Path(record["previous_export"]) / "index.html").read_text())
        self.assertEqual(["docker","network","disconnect"],commands.call_args_list[2].args[0][:3])
        self.assertEqual([],build.build_freshness_errors(self.project))

    def test_unsupported_selection_is_blocked_without_tool_call(self):
        decision = self.project / "technology-decision.md"
        decision.write_text("EXECUTION_PROFILE: server-runtime\nREQUIRED_EXTERNAL_SERVICES: NONE\n")
        self.assertTrue(build.technology_execution_errors(self.project))
        decision.write_text("EXECUTION_PROFILE: npm-static-export\nREQUIRED_EXTERNAL_SERVICES: database\n")
        self.assertTrue(build.technology_execution_errors(self.project))
        decision.write_text("EXECUTION_PROFILE: npm-static-export\nREQUIRED_EXTERNAL_SERVICES: NONE\n")
        self.assertTrue(build.technology_execution_errors(self.project))

    def test_export_rejects_archive_escape_and_links(self):
        for name, kind in [("../escape",tarfile.REGTYPE),("file:stream",tarfile.REGTYPE),("link",tarfile.SYMTYPE)]:
            with self.subTest(name=name):
                payload = io.BytesIO()
                with tarfile.open(fileobj=payload,mode="w") as archive:
                    entry = tarfile.TarInfo(name)
                    entry.type = kind
                    entry.linkname = "../outside" if kind == tarfile.SYMTYPE else ""
                    archive.addfile(entry)
                class Process:
                    stdout = io.BytesIO(payload.getvalue())
                    def poll(self): return 0
                    def wait(self,timeout=None): return 0
                    def kill(self): pass
                with patch.object(build.subprocess,"Popen",return_value=Process()):
                    with self.assertRaisesRegex(ValueError,"invalid export"):
                        build.copy_export("docker","awd-test","out",self.project)
