"""MCP handoff boundaries; real Blender/browser probe is explicitly opt-in."""
import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import harness_mcp_server as mcp
from harness_blender import import_blender_file, inspect_blender_asset
from validation_blender import blender_handoff_errors, blender_delivery_errors


class BlenderRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        started = mcp.harness.start_chat_run(None, Path(self.temp.name), None, "A crafted lighting landing")
        self.project = Path(started["project_dir"])
        self.run = Path(started["run_dir"])
        self.active = {"stage": "production-plan", "agent": "05"}
        self.context = patch.object(mcp, "_project_and_stage", return_value=(self.run, self.active, self.project))
        self.context.start()
        self.addCleanup(self.context.stop)
        config = json.loads((self.project / "project.config.json").read_text())
        config["implementation_root"] = "implementation"
        (self.project / "project.config.json").write_text(json.dumps(config))
        (self.project / "production-plan.md").write_text(
            "### 3D production provenance\n\n| FX ID | Medium | External source / authoring tool | Asset / runtime | Rights | Integration | Fallback |\n"
            "|---|---|---|---|---|---|---|\n| FX-001 | INTERACTIVE_3D | Blender / CUSTOM | model.glb | own | app.js#model | poster.png |\n\n"
            "BLENDER_HANDOFF:\n", encoding="utf-8")
        self.args = {"run_id": self.run.name, "fx_id": "FX-001"}

    def upload(self, role, data):
        return import_blender_file(mcp, self.args | {"role": role, "data_base64": base64.b64encode(data).decode()})

    def test_only_declared_fx_and_production_can_import(self):
        self.active["stage"] = "definition"
        with self.assertRaisesRegex(ValueError, "production-plan"):
            self.upload("builder", b"# never run")
        self.active["stage"] = "production-plan"
        self.args["fx_id"] = "FX-999"
        with self.assertRaisesRegex(ValueError, "declare"):
            self.upload("builder", b"# never run")

    def test_no_client_receipt_and_no_header_only_raster(self):
        with self.assertRaisesRegex(ValueError, "role"):
            self.upload("inspection", b'{"exit_code":0}')
        with self.assertRaises(Exception):
            self.upload("preview", b"\x89PNG\r\n\x1a\ninvalid")

    def test_import_invalidates_inspection_and_preserves_old_files(self):
        first = self.upload("builder", b"# one")
        second = self.upload("builder", b"# two")
        self.assertNotEqual(first["path"], second["path"])
        self.assertTrue((self.project / first["path"]).is_file())
        self.assertTrue(blender_handoff_errors(self.project))
        with self.assertRaises(ValueError):
            mcp._write_allowed(self.project, "production-plan", "evidence/blender/handoff.json")

    @unittest.skipUnless(os.getenv("AGENTIC_RUN_BLENDER_TESTS") == "1", "real Blender/browser probe opt-in")
    def test_real_import_inspection_browser_binding_and_tamper(self):
        fixture = Path(os.environ["AGENTIC_BLENDER_FIXTURE"])
        for role, name in {"scene":"sample.blend", "builder":"builder.py", "preview":"preview.png", "export":"sample.glb"}.items():
            self.upload(role, (fixture / name).read_bytes())
        result = inspect_blender_asset(mcp, self.args)
        self.assertEqual([], blender_handoff_errors(self.project))
        from harness_blender import preserve_blender_assets
        rebuilt = self.project / "rebuilt"
        rebuilt.mkdir()
        preserve_blender_assets(self.project, rebuilt)
        delivered = result["asset"]["delivery"]
        self.assertEqual(delivered["sha256"], sha256((rebuilt / delivered["path"]).read_bytes()).hexdigest())
        (rebuilt / delivered["path"]).write_bytes(b"conflicting model")
        with self.assertRaisesRegex(ValueError, "conflicts"):
            preserve_blender_assets(self.project, rebuilt)
        self.assertTrue(blender_delivery_errors(self.project, self.project / "implementation"))
        probe = ROOT / ".harness/blender-web-probe/site"
        site = self.project / "implementation"
        shutil.copytree(probe / "vendor", site / "vendor")
        (site / "index.html").write_bytes((probe / "index.html").read_bytes())
        (site / "preview.png").write_bytes((fixture / "preview.png").read_bytes())
        path = result["asset"]["delivery"]["path"]
        (site / "app.js").write_text((probe / "app.js").read_text(encoding="utf-8").replace('./sample.glb', './' + path), encoding="utf-8")
        from harness_render import render_static
        capture = render_static(self.project, site, "index.html", [], [{"type":"tab"}, {"type":"reduced-motion"}])
        self.assertFalse(any(item.get("errors") for item in capture["captures"]))
        desktop = [item for item in capture["captures"] if item["viewport"] == "desktop" and item["kind"] == "interaction"]
        self.assertIn('"mode":"webgl"', desktop[0]["observed"]["visibleText"])
        self.assertIn("3D activo", desktop[0]["observed"]["visibleText"])
        self.assertIn("estática", desktop[1]["observed"]["visibleText"])
        self.assertEqual([], blender_delivery_errors(self.project, site))
        original = (site / path).read_bytes()
        (site / path).write_bytes(original + b"changed")
        self.assertTrue(any("differ" in error for error in blender_delivery_errors(self.project, site)))
        # A client cannot substitute its own success report for real Blender import.
        self.upload("scene", b"BLENDER-v500not-a-real-scene")
        with self.assertRaises(RuntimeError):
            inspect_blender_asset(mcp, self.args)
        self.assertTrue(blender_handoff_errors(self.project))


if __name__ == "__main__":
    unittest.main()
