from __future__ import annotations

import base64
import json
import os
import subprocess
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
    def test_stdio_uses_utf8_even_with_legacy_windows_encoding(self):
        name = "iluminación → 日本語"
        request = {"jsonrpc": "2.0", "id": 41, "method": "tools/call",
                   "params": {"name": name, "arguments": {}}}
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "harness_mcp_server.py"),
             "--transport", "stdio"],
            input=(json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"),
            capture_output=True, timeout=15,
            env={**os.environ, "PYTHONIOENCODING": "cp1252"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(response["id"], 41)
        self.assertTrue(response["result"]["isError"])
        self.assertIn(name, response["result"]["structuredContent"]["error"])

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.previous_root = mcp.RUNS_ROOT
        mcp.RUNS_ROOT = Path(self.temp.name).resolve()
        self.readiness = patch("harness_operations.runtime_status", return_value={"ready_for_live_probe":True,"checks":{}})
        self.readiness.start()

    def tearDown(self) -> None:
        mcp.RUNS_ROOT = self.previous_root
        self.readiness.stop()
        self.temp.cleanup()

    def start(self) -> dict:
        return mcp.start_landing({"brief": "Create a distinctive premium landing for a real local business."})

    def test_mcp_lists_the_managed_pipeline_tools(self):
        response = mcp.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {item["name"] for item in response["result"]["tools"]}
        self.assertIn('confirm_design', names)
        names.remove('confirm_design')
        self.assertEqual(
            names,
            {"start_landing", "get_stage", "list_files", "read_file", "get_guidance", "write_file", "generate_image", "register_image", "register_session_image", "confirm_master", "advance_stage", "verify_run", "runtime_status", "read_image", "upload_image", "render_landing", "run_review", "prepare_delivery", "download_delivery", "check_technology", "build_frontend", "import_blender_file", "inspect_blender_asset"},
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

    def test_review_revision_returns_owner_once_without_advancing(self):
        started = self.start()
        project = Path(started["project_dir"])
        reviews = project / ".reviews"
        reviews.mkdir()
        record = reviews / "direction-review.json"
        budget = reviews / "direction-review-attempts.json"
        record.write_text(json.dumps({"result": {"verdict": "REVISE", "correction_kind":"CRAFT", "findings": ["Add type specimen"]}}))
        budget.write_text(json.dumps({"count": 1}))
        active = {**started, "stage": "direction-review", "agent": "07", "mode": "direction-review"}
        state = (project / "status.json").read_bytes()
        with patch.object(mcp, "_project_and_stage", return_value=(Path(started["run_dir"]), active, project)), \
             patch("harness_review.review_record_errors", return_value=["revision required"]), \
             patch.object(mcp, "build_stage_packet", return_value={"specialist": "03"}):
            result = mcp.advance_stage({"run_id": started["run_id"]})
            self.assertEqual(result["status"], "REVISE")
            self.assertEqual(result["stage_packet"]["specialist"], "03")
            self.assertEqual(result["stage_packet"]["findings"], ["Add type specimen"])
            self.assertEqual(result['stage_packet']['correction_kind'], 'CRAFT')
            self.assertEqual((project / "status.json").read_bytes(), state)
            budget.write_text(json.dumps({"count": 2}))
            self.assertEqual(mcp.advance_stage({"run_id": started["run_id"]})["status"], "BLOCKED")
        from harness_review import revision_stage
        record.write_text(json.dumps({"result": {"verdict": "PASS", "findings": []}}))
        self.assertIsNone(revision_stage(project, "direction-review"))

    def test_validation_exception_restores_state(self):
        started = self.start()
        state = Path(started["project_dir"]) / "status.json"
        before = state.read_bytes()
        with patch.object(mcp.harness, "advance_chat_run", side_effect=RuntimeError("validator crashed")):
            with self.assertRaisesRegex(RuntimeError, "validator crashed"):
                mcp.advance_stage({"run_id": started["run_id"]})
        self.assertEqual(state.read_bytes(), before)

    def test_reference_failure_packet_has_no_owner_write_authority(self):
        started = self.start()
        project = Path(started['project_dir'])
        (project / '.reviews').mkdir()
        (project / '.reviews/direction-review.json').write_text(json.dumps({'result':{
            'verdict':'REVISE','correction_kind':'REFERENCE','findings':['Benchmark does not fit available proof']}}))
        active = {**started,'stage':'direction-review'}
        packet = mcp._with_stage_packet(active)['stage_packet']
        self.assertEqual([], packet['writable_files'])
        self.assertEqual('REFERENCE', packet['correction_kind'])
        self.assertIn('Escalate', packet['completion_protocol'][0])

    def test_design_preflight_keeps_owner_and_state(self):
        started = self.start()
        project = Path(started["project_dir"])
        active = {**started, "stage":"visual-experience", "agent":"04", "mode":"visual-experience"}
        before = (project / "status.json").read_bytes()
        with patch.object(mcp, "_project_and_stage", return_value=(Path(started["run_dir"]), active, project)), \
             patch("harness_review.design_preflight_errors", return_value=["missing media decision"]), \
             patch.object(mcp.harness, "advance_chat_run") as advance:
            result = mcp.advance_stage({"run_id":started["run_id"]})
        self.assertEqual("REVISE", result["status"])
        self.assertEqual("04", result["stage_packet"]["specialist"])
        self.assertEqual(before, (project / "status.json").read_bytes())
        advance.assert_not_called()

    def test_complete_design_waits_for_user_without_advancing(self):
        started = self.start()
        project = Path(started['project_dir'])
        active = {**started, 'stage':'design-review', 'agent':'07', 'mode':'design-review'}
        before = (project / 'status.json').read_bytes()
        with patch.object(mcp, '_project_and_stage', return_value=(Path(started['run_dir']), active, project)), \
             patch('harness_review.review_record_errors', return_value=[]), \
             patch.object(mcp, 'complete_stage_status') as complete:
            result = mcp.advance_stage({'run_id':started['run_id']})
        self.assertEqual('NEEDS_USER', result['status'])
        self.assertIn('confirm_design', result['instruction'])
        self.assertEqual(before, (project / 'status.json').read_bytes())
        complete.assert_not_called()

    def test_new_flow_rejects_early_master_approval(self):
        started = self.start()
        with self.assertRaisesRegex(ValueError, 'complete landing'):
            mcp.confirm_master({'run_id':started['run_id'], 'status':'APPROVED', 'user_signal':'yes'})

    def test_empty_research_cannot_advance_to_content(self):
        self.test_orchestrator_advances_one_valid_stage_and_owns_state()
        run = next(path for path in mcp.RUNS_ROOT.iterdir() if path.is_dir())
        state = (run / "project" / "status.json").read_bytes()
        result = mcp.advance_stage({"run_id": run.name})
        self.assertEqual(result["status"], "REVISE")
        self.assertEqual(result["stage"], "research-strategy")
        self.assertEqual((run / "project" / "status.json").read_bytes(), state)

    def test_late_transition_failure_restores_journal_and_state(self):
        from harness_transition import TRANSITION_FILES
        for failing_operation in ("snapshot", "activation", "packet"):
            with self.subTest(operation=failing_operation):
                started = self.start()
                run = Path(started["run_dir"])
                originals = {name: (run / name).read_bytes() if (run / name).is_file() else None
                             for name in TRANSITION_FILES}
                target, method = {
                    "snapshot": (mcp.harness, "_save_chat_snapshot"),
                    "activation": (mcp, "activate_stage_status"),
                    "packet": (mcp, "_with_stage_packet"),
                }[failing_operation]
                # Bypass content checks only to reach the late transaction faults.
                with patch.object(mcp.harness, "stage_readiness_errors", return_value=[]), \
                     patch.object(target, method, side_effect=RuntimeError("late failure")):
                    with self.assertRaisesRegex(RuntimeError, "late failure"):
                        mcp.advance_stage({"run_id": run.name})
                for name, before in originals.items():
                    path = run / name
                    self.assertEqual(path.read_bytes() if path.is_file() else None, before, name)
                self.assertEqual(mcp.get_stage({"run_id": run.name})["stage"], "definition")

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
                self.assertIn("INDEPENDENT_REVIEW_REQUIRED", result["findings"][0])

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
        with patch.dict("os.environ", {"AGENTIC_IMAGE_MODEL":"test-image-model"}):
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
