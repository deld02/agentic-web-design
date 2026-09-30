"""No-key backend: no API calls, honest media provenance and fresh review dispatch."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import harness_mcp_server as mcp
import harness_session as session
from harness_review import run_visual_review, review_record_errors
from validation_image_generation import is_image_generation_event, missing_generation_receipts


class SessionBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.env = patch.dict(os.environ, {"AGENTIC_AI_BACKEND": "session", "OPENAI_API_KEY": "", "CODEX_API_KEY": ""})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def picture(self, project, name):
        from PIL import Image
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (32, 32), "blue").save(path)
        return path

    def test_native_generation_returns_instruction_not_fake_success(self):
        with patch.object(mcp, "_project_and_stage", return_value=(self.root,{"stage":"creative-master"},self.root)), \
             patch.object(mcp, "_image_output",return_value=self.root / "master.png"), \
             patch.object(mcp, "_openai_image") as api:
            result = mcp.generate_image.__wrapped__({"run_id":"test", "prompt":"An editorial image made for this specific exhibition project."})
        self.assertEqual("NEEDS_NATIVE_IMAGE", result["status"])
        api.assert_not_called()

    def test_start_without_api_preserves_session_profile(self):
        with patch.object(mcp, "RUNS_ROOT", self.root), \
             patch("harness_operations.runtime_status", return_value={"ready_for_live_probe":True}):
            result = mcp.start_landing({"brief":"An exhibition landing for visitors"})
        self.assertEqual("session", json.loads((Path(result["run_dir"])/"run.json").read_text())["ai_backend"])
        self.assertEqual("definition",result["stage"])

    def test_native_receipt_needs_run_hash_and_reference(self):
        project = self.root / "project"
        project.mkdir()
        path = self.picture(project,"assets/master.png")
        from harness_media import inspect_raster
        (self.root / "run.json").write_text('{"ai_backend":"session"}')
        event = {"event":"tool_call", "tool":"SESSION_IMAGE_RESULT", "provenance":"CLIENT_ATTESTED",
                 "file":"assets/master.png", "tool_call_reference":"native-tool-result-123",
                 "sha256":inspect_raster(path.read_bytes(),".png")["sha256"]}
        self.assertTrue(is_image_generation_event(event,project))
        self.assertFalse(is_image_generation_event(event))
        self.assertFalse(is_image_generation_event(event | {"sha256":"wrong"},project))
        self.assertFalse(is_image_generation_event(event | {"tool_call_reference":""},project))
        (self.root / "run.json").write_text('{"ai_backend":"api"}')
        self.assertFalse(is_image_generation_event(event,project))

    def test_not_logged_in_never_falls_back(self):
        with patch.object(session,"codex_status",return_value={"chatgpt_login":False}), \
             patch.object(session.subprocess,"Popen") as run:
            with self.assertRaisesRegex(RuntimeError,"codex login"):
                session.subscription_review({},[],{},[])
        run.assert_not_called()

    def test_session_review_shares_validation_and_staleness(self):
        result = mcp.harness.start_chat_run(None,self.root,None,"A visitor exhibition landing")
        project = Path(result["project_dir"])
        for path in (project / "project.config.json", project.parent / "run.json"):
            metadata = json.loads(path.read_text())
            metadata.pop("design_contract", None)
            path.write_text(json.dumps(metadata))
        images = ["evidence/desktop.png","evidence/mobile.png"]
        for name in images:
            self.picture(project,name)
        axes = ["composition","typography","color","media_integration","project_fit","reference_calibration","artistic_authority"]
        verdict = {"verdict":"PASS","summary":"test only","selected_direction":"","findings":[],
                   "correction_kind":"NONE",
                   "axes":{axis:{"status":"PASS","evidence":images[0]+" versus "+images[1]+": visible fixture"} for axis in axes}}
        response = {"status":"completed","id":"codex-thread-test",
                    "output":[{"content":[{"type":"output_text","text":json.dumps(verdict)}]}]}
        stage = next(s for s in mcp.load_json(mcp.ROOT / "config/pipeline.json")["stages"] if s["id"]=="design-review")
        with patch("validation_landing_blueprint.complete_landing_flow", return_value=False), \
             patch("harness_review.benchmark_images", return_value=[images[1]]), \
             patch("project_validation.scene_visual_errors", return_value=[]), \
             patch("project_validation.page_rhythm_errors", return_value=[]), \
             patch("validation_spatial_experience.spatial_selection_errors", return_value=[]), \
             patch("harness_review.subscription_review",return_value=response) as native, \
             patch("urllib.request.urlopen") as api:
            record = run_visual_review(mcp.ROOT,project,stage,images)
        self.assertEqual("CODEX_SUBSCRIPTION",record["provider"])
        api.assert_not_called()
        native.assert_called_once()
        self.assertEqual([],review_record_errors(project,"design-review"))
        (project/"visual-system.md").write_text("changed")
        self.assertTrue(review_record_errors(project,"design-review"))

    def test_unknown_backend_rejected(self):
        with patch.dict(os.environ,{"AGENTIC_AI_BACKEND":"typo"}):
            with self.assertRaises(ValueError): session.session_mode()

    @unittest.skipUnless(os.getenv("AGENTIC_RUN_SESSION_TESTS") == "1", "subscription live probe opt-in")
    def test_live_subscription_review(self):
        from harness_review import _schema
        image = self.picture(self.root, "desktop.png")
        result = session.subscription_review({"stage":"design-review", "note":"Synthetic blue square test, not a finished landing. Review it honestly."},
                                             [image], _schema(["composition"]), ["desktop.png"])
        self.assertEqual("completed", result["status"])
        self.assertTrue(result["id"])
        verdict = json.loads(result["output"][0]["content"][0]["text"])
        self.assertIn(verdict["verdict"], {"PASS","REVISE"})
        self.assertIn("desktop.png", verdict["axes"]["composition"]["evidence"])
