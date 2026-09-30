import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import harness_mcp_server as mcp
from harness_operations import runtime_status
from harness_review import run_visual_review
from harness_render import render_static


class RuntimeRepairTests(unittest.TestCase):
    def test_subscription_login_is_a_readiness_requirement(self):
        with patch.dict(os.environ, {"AGENTIC_AI_BACKEND":"session"}), \
             patch("harness_operations.codex_status", return_value={"available":True,"chatgpt_login":False}):
            result = runtime_status(mcp, {})
        self.assertFalse(result["ready_for_live_probe"])
        self.assertFalse(result["checks"]["subscription_reviewer_ready"])
        self.assertIn("blender", result)
        self.assertNotIn("blender", result["checks"])

    def test_render_uses_utf8_not_windows_locale(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text("<h1>Dirección y composición</h1>", encoding="utf-8")
            with patch("harness_render.shutil.which", return_value="node"), \
                 patch("harness_render.subprocess.run", return_value=Mock(returncode=0, stdout='{"captures":[]}')) as call:
                render_static(root, root, "index.html", [])
            self.assertEqual("utf-8", call.call_args.kwargs["encoding"])

    def test_provider_failures_do_not_spend_design_reviews(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            started = mcp.harness.start_chat_run(None, Path(directory), None, "An exhibition landing")
            project = Path(started["project_dir"])
            for path in (project.parent/'run.json',project/'project.config.json'):
                data=json.loads(path.read_text(encoding='utf-8'));data.pop('design_contract',None)
                path.write_text(json.dumps(data),encoding='utf-8')
            images = ["desktop.png", "mobile.png"]
            for name in images:
                Image.new("RGB", (32,32)).save(project / name)
            stage = next(s for s in mcp.load_json(ROOT / "config/pipeline.json")["stages"] if s["id"] == "design-review")
            axes = ["composition", "typography", "color", "media_integration", "project_fit", "reference_calibration", "artistic_authority"]
            verdict = {"verdict":"PASS", "summary":"fixture", "selected_direction":"", "findings":[],
                       "correction_kind":"NONE",
                       "axes":{a:{"status":"PASS","evidence":"desktop.png versus mobile.png: visible fixture"} for a in axes}}
            response = {"status":"completed", "id":"test-thread", "output":[{"content":[{"type":"output_text", "text":json.dumps(verdict)}]}]}
            with patch("validation_landing_blueprint.complete_landing_flow", return_value=False), \
                 patch("harness_review.benchmark_images", return_value=[images[1]]), \
                 patch("project_validation.scene_visual_errors", return_value=[]), \
                 patch("validation_spatial_experience.spatial_selection_errors", return_value=[]), \
                 patch.dict(os.environ, {"AGENTIC_AI_BACKEND":"session"}), \
                 patch("harness_review.subscription_review", side_effect=[RuntimeError("offline"), RuntimeError("timeout"), response]):
                for _ in range(2):
                    with self.assertRaises(RuntimeError):
                        run_visual_review(ROOT, project, stage, images)
                budget = project / ".reviews/design-review-attempts.json"
                self.assertEqual({"count":0,"calls":2}, json.loads(budget.read_text()))
                run_visual_review(ROOT, project, stage, images)
                self.assertEqual({"count":1,"calls":3}, json.loads(budget.read_text()))
