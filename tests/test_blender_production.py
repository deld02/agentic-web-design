import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validation_blender import blender_handoff_errors
from validation_capability_activation import stage_activation_errors
from validation_spatial_experience import spatial_plan_errors
from stage_orchestrator import capability_guidance


class BlenderProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)

    def fixture(self, medium="INTERACTIVE_3D", source="Blender / CUSTOM"):
        (self.project / "production-plan.md").write_text(
            "### 3D production provenance\n\n"
            "| FX ID | Medium | External source / authoring tool | Asset / runtime | License or rights | Integration proof | Fallback |\n"
            "|---|---|---|---|---|---|---|\n"
            f"| FX-001 | {medium} | {source} | lamp.glb | own work | index.html#lamp | lamp.png |\n\n"
            "BLENDER_HANDOFF: evidence/blender/handoff.json\n", encoding="utf-8")
        report = {"blender_version": "test-fixture", "command": "synthetic fixture, not real execution", "exit_code": 0, "fresh_import": True}
        data = {
            "scene": ("lamp.blend", b"BLENDER-v500fixture"),
            "builder": ("builder.py", b"# synthetic builder fixture\n"),
            "preview": ("preview.png", b"\x89PNG\r\n\x1a\nfixture"),
            "inspection": ("evidence/blender/FX-001/inspection-fixture/receipt.json", json.dumps(report).encode()),
            "export": ("lamp.glb", b"glTF" + struct.pack("<II", 2, 20) + b"12345678"),
        }
        files = {}
        for role, (name, content) in data.items():
            (self.project / name).parent.mkdir(parents=True, exist_ok=True)
            (self.project / name).write_bytes(content)
            files[role] = {"path": name, "sha256": hashlib.sha256(content).hexdigest()}
        payload = {"assets": [{"fx_id": "FX-001", "files": files}]}
        self.save(payload)
        return payload

    def save(self, payload):
        target = self.project / "evidence/blender/handoff.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload), encoding="utf-8")

    def test_non_blender_projects_have_no_extra_requirement(self):
        self.assertEqual([], blender_handoff_errors(self.project))
        self.fixture(source="Blender / EXISTING_ASSET")
        (self.project / "evidence/blender/handoff.json").unlink()
        self.assertEqual([], blender_handoff_errors(self.project))

    def test_custom_route_requires_physical_manifest_through_spatial_gate(self):
        self.fixture()
        (self.project / "evidence/blender/handoff.json").unlink()
        self.assertTrue(any("BLENDER_HANDOFF" in e for e in spatial_plan_errors(self.project)))

    def test_old_structural_fixture_cannot_claim_server_inspection(self):
        self.fixture()
        self.assertTrue(any("inspect_blender_asset" in e for e in blender_handoff_errors(self.project)))

    def test_stale_export_blocks(self):
        self.fixture()
        (self.project / "lamp.glb").write_bytes(b"changed")
        self.assertTrue(any("SHA-256" in e for e in blender_handoff_errors(self.project)))

    def test_rendered_route_does_not_require_glb(self):
        payload = self.fixture("RENDERED_3D")
        del payload["assets"][0]["files"]["export"]
        self.save(payload)
        self.assertFalse(any("export" in e for e in blender_handoff_errors(self.project)))

    def test_interactive_requires_export_and_fresh_import(self):
        payload = self.fixture()
        del payload["assets"][0]["files"]["export"]
        report = json.dumps({"blender_version": "test", "command": "test", "exit_code": 0, "fresh_import": False}).encode()
        (self.project / payload["assets"][0]["files"]["inspection"]["path"]).write_bytes(report)
        payload["assets"][0]["files"]["inspection"]["sha256"] = hashlib.sha256(report).hexdigest()
        self.save(payload)
        errors = blender_handoff_errors(self.project)
        self.assertTrue(any("export" in e for e in errors))
        self.assertTrue(any("fresh-import" in e for e in errors))

    def test_paths_cannot_escape_project(self):
        payload = self.fixture()
        payload["assets"][0]["files"]["builder"]["path"] = "../outside.py"
        self.save(payload)
        self.assertTrue(any("outside project" in e for e in blender_handoff_errors(self.project)))

    def test_svg_cannot_substitute_blender_render(self):
        payload = self.fixture()
        data = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        (self.project / "fake.svg").write_bytes(data)
        payload["assets"][0]["files"]["preview"] = {"path": "fake.svg", "sha256": hashlib.sha256(data).hexdigest()}
        self.save(payload)
        self.assertTrue(any("raster preview" in e for e in blender_handoff_errors(self.project)))

    def test_invalid_manifest_does_not_crash(self):
        self.fixture()
        for payload in ([], {"assets": [None]}, {"assets": [{"fx_id": []}]}):
            self.save(payload)
            self.assertTrue(blender_handoff_errors(self.project))

    def test_selected_custom_route_requires_capability_log(self):
        self.fixture()
        self.assertTrue(any("blender-asset-production" in e for e in stage_activation_errors(self.project, ROOT, "production-plan")))
        with (self.project / "production-plan.md").open("a", encoding="utf-8") as file:
            file.write("\n## Design capability log\n\n| Capability | Mode |\n|---|---|\n| blender-asset-production | production-plan |\n")
        self.assertFalse(any("blender-asset-production" in e for e in stage_activation_errors(self.project, ROOT, "production-plan")))

    def test_capability_is_available_only_in_production_related_stages(self):
        result = capability_guidance(ROOT, "production-plan", "blender-asset-production")
        self.assertTrue(result)
        with self.assertRaises(ValueError):
            capability_guidance(ROOT, "definition", "blender-asset-production")


if __name__ == "__main__":
    unittest.main()
