from __future__ import annotations

import base64
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import harness_mcp_server as mcp  # noqa: E402
from validation_user_authority import record_master_confirmation  # noqa: E402


class _ImageResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        raster = base64.b64encode(b"\x89PNG\r\n\x1a\nphysical").decode("ascii")
        return json.dumps({"data": [{"b64_json": raster}]}).encode("utf-8")


class HarnessMcpServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.previous_root = mcp.RUNS_ROOT
        mcp.RUNS_ROOT = Path(self.temp.name).resolve()

    def tearDown(self) -> None:
        mcp.RUNS_ROOT = self.previous_root
        self.temp.cleanup()

    def start(self) -> dict:
        return mcp.start_landing({"brief": "Create a distinctive premium landing for a real local business."})

    def test_mcp_lists_the_managed_pipeline_tools(self):
        response = mcp.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {item["name"] for item in response["result"]["tools"]}
        self.assertEqual(
            names,
            {"start_landing", "get_stage", "list_files", "read_file", "get_guidance", "write_file", "generate_image", "register_image", "confirm_master", "advance_stage", "verify_run"},
        )

    def test_initialize_places_pipeline_order_in_server_instructions(self):
        response = mcp.dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        instructions = response["result"]["instructions"]
        self.assertIn("call start_landing", instructions)
        self.assertIn("never work ahead", instructions)
        self.assertLessEqual(len(instructions), 512)

    def test_run_starts_at_definition_and_blocks_work_ahead(self):
        started = self.start()
        self.assertEqual(started["stage"], "definition")
        self.assertEqual(started["stage_packet"]["specialist"], "00")
        self.assertIn("MISIÓN", started["stage_packet"]["contract"]["text"])
        with self.assertRaisesRegex(ValueError, "not writable during definition"):
            mcp.write_file({"run_id": started["run_id"], "path": "creative-direction.md", "text": "too early"})

    def test_specialists_cannot_write_or_forge_official_state(self):
        started = self.start()
        with self.assertRaisesRegex(ValueError, "not writable during definition"):
            mcp.write_file({"run_id": started["run_id"], "path": "status.json", "text": "{}"})

    def test_rejected_stage_never_leaves_approved_state(self):
        started = self.start()
        state = Path(started["project_dir"]) / "status.json"
        before = state.read_bytes()
        result = mcp.advance_stage({"run_id": started["run_id"]})
        self.assertEqual(result["status"], "REVISE")
        self.assertEqual(state.read_bytes(), before)
        result = mcp.advance_stage({"run_id": started["run_id"]})
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(state.read_bytes(), before)
        self.assertEqual(mcp.get_stage({"run_id": started["run_id"]})["status"], "FAILED")

    def test_validation_exception_restores_state(self):
        started = self.start()
        state = Path(started["project_dir"]) / "status.json"
        before = state.read_bytes()
        with patch.object(mcp.harness, "advance_chat_run", side_effect=RuntimeError("validator crashed")):
            with self.assertRaisesRegex(RuntimeError, "validator crashed"):
                mcp.advance_stage({"run_id": started["run_id"]})
        self.assertEqual(state.read_bytes(), before)

    def test_implementation_root_cannot_grant_state_access(self):
        started = self.start()
        project = Path(started["project_dir"])
        original = (project / "project.config.json").read_bytes()
        for value in (".", "..", str(project), "assets", "implementation/.."):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "implementation_root"):
                    mcp.write_file({"run_id": started["run_id"], "path": "project.config.json",
                                    "text": json.dumps({"implementation_root": value})})
                self.assertEqual((project / "project.config.json").read_bytes(), original)
        mcp.write_file({"run_id": started["run_id"], "path": "project.config.json",
                        "text": json.dumps({"implementation_root": "implementation"})})
        for target in ("status.json", "brief.md", "implementation/../status.json"):
            with self.assertRaises(ValueError):
                mcp._write_allowed(project, "implementation", target)
        self.assertEqual(mcp._write_allowed(project, "implementation", "implementation/index.html"),
                         project / "implementation" / "index.html")

    def test_reviews_cannot_self_approve_or_rewrite_owner(self):
        started = self.start()
        project = Path(started["project_dir"])
        stages = mcp.load_json(ROOT / "config" / "pipeline.json")["stages"]
        for stage_id, artifact in (("direction-review", "creative-direction.md"),
                                   ("design-review", "visual-system.md"),
                                   ("build-review", "qa-release.md")):
            stage = next(item for item in stages if item["id"] == stage_id)
            with self.assertRaises(ValueError):
                mcp._write_allowed(project, stage_id, artifact)
            with self.assertRaisesRegex(ValueError, "isolated executor"):
                mcp.complete_stage_status(project, stage, [])
            active = {**started, "stage": stage_id, "agent": "07"}
            with patch.object(mcp, "_project_and_stage", return_value=(Path(started["run_dir"]), active, project)):
                result = mcp.advance_stage({"run_id": started["run_id"]})
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIn("INDEPENDENT_REVIEW_UNAVAILABLE", result["findings"][0])

    def test_orchestrator_advances_one_valid_stage_and_owns_state(self):
        started = self.start()
        brief = mcp.read_file({"run_id": started["run_id"], "path": "brief.md"})["text"]
        brief = brief.replace(
            "## Objective, audience and primary action\n",
            "## Objective, audience and primary action\n\nHelp a real local business earn qualified enquiries from decision makers.\n",
            1,
        ).replace(
            "## Project type and provisional scope\n",
            "## Project type and provisional scope\n\nOne responsive landing with a clear contact action.\n",
            1,
        )
        mcp.write_file({"run_id": started["run_id"], "path": "brief.md", "text": brief})
        advanced = mcp.advance_stage({"run_id": started["run_id"]})
        self.assertEqual(advanced["stage"], "research-strategy")
        self.assertEqual(advanced["stage_packet"]["specialist"], "01")
        status = json.loads((Path(started["project_dir"]) / "status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["gates"]["G0"]["status"], "APPROVED")
        self.assertEqual(status["checkpoints"]["research-strategy"]["status"], "ACTIVE")

    def test_stage_packet_contains_inputs_and_bounded_conditional_guidance(self):
        started = self.start()
        with self.assertRaisesRegex(ValueError, "unavailable"):
            mcp.get_guidance({"run_id": started["run_id"], "capability_id": "emil-motion-craft"})

    def test_packet_does_not_repeat_shared_guidance_or_artifacts(self):
        started = self.start()
        stages = mcp.load_json(ROOT / "config" / "pipeline.json")["stages"]
        for stage in stages:
            packet = mcp.build_stage_packet(ROOT, Path(started["project_dir"]), stage,
                                            mcp.STAGE_FILES[stage["id"]])
            self.assertFalse(set(packet["current_artifacts"]) & set(packet["required_inputs"]))
            loaded = [item["reference"] for item in packet["capabilities"]["automatic"] if "guidance" in item]
            self.assertEqual(len(loaded), len(set(loaded)))

    def test_active_owner_artifact_can_be_written(self):
        started = self.start()
        result = mcp.write_file({"run_id": started["run_id"], "path": "brief.md", "text": "# Managed brief\n"})
        self.assertEqual(result["status"], "WRITTEN")
        self.assertEqual(result["stage"], "definition")

    def test_path_traversal_is_rejected(self):
        started = self.start()
        with self.assertRaisesRegex(ValueError, "escapes"):
            mcp.read_file({"run_id": started["run_id"], "path": "../run.json"})

    def test_image_api_helper_requires_physical_base64_data(self):
        raster = mcp._openai_image("A sufficiently specific project visual prompt", "secret", opener=lambda *_args, **_kwargs: _ImageResponse())
        self.assertTrue(raster.startswith(b"\x89PNG"))

    def test_master_confirmation_only_changes_checkpoint_fields(self):
        artifact = Path(self.temp.name) / "creative-direction.md"
        artifact.write_text(
            "# Direction\n\n## Artistic master confirmation\nCHECKPOINT: artistic master confirmation\nSTATUS: PENDING\nPRESENTED_MASTER: AM-001\nUSER_SIGNAL:\n",
            encoding="utf-8",
        )
        result = record_master_confirmation(artifact, "APPROVED", "Me gusta esta\ndirección")
        text = artifact.read_text(encoding="utf-8")
        self.assertEqual(result["status"], "APPROVED")
        self.assertIn("PRESENTED_MASTER: AM-001", text)
        self.assertIn("USER_SIGNAL: Me gusta esta dirección", text)


if __name__ == "__main__":
    unittest.main()
