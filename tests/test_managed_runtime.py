"""Runtime integration tests; provider responses are simulated, not visual QA."""

import base64
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import harness_mcp_server as mcp
from harness_transition import transition_rollback
from harness_review import run_visual_review, review_record_errors


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.root_patch = patch.object(mcp, "RUNS_ROOT", self.root)
        self.root_patch.start()
        self.started = mcp.harness.start_chat_run(None, self.root, None, "A static craft exhibition landing for visitors.")
        self.run = Path(self.started["run_dir"])
        self.project = Path(self.started["project_dir"])

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    def test_start_reports_missing_runtime_before_creating_run(self):
        before = sorted(path.name for path in self.root.iterdir() if path.is_dir())
        with patch("harness_operations.runtime_status", return_value={"ready_for_live_probe":False,"checks":{"api":False}}):
            result = mcp.start_landing({"brief":"A landing that must not begin without capabilities"})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertNotIn("run_id", result)
        self.assertEqual(before, sorted(path.name for path in self.root.iterdir() if path.is_dir()))

    def test_interrupted_transition_is_recovered_on_next_read(self):
        state = self.project / "status.json"
        before = state.read_bytes()
        with self.assertRaises(KeyboardInterrupt):
            with transition_rollback(self.run):
                state.write_text("interrupted mutation", encoding="utf-8")
                raise KeyboardInterrupt()
        self.assertTrue((self.run / "control/transition.json").exists())
        result = mcp.get_stage({"run_id":self.run.name})
        self.assertEqual(result["stage"], "definition")
        self.assertEqual(state.read_bytes(), before)
        self.assertFalse((self.run / "control/transition.json").exists())

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow required")
    def test_header_only_png_is_rejected(self):
        from harness_media import inspect_raster
        with self.assertRaises(Exception):
            inspect_raster(b"\x89PNG\r\n\x1a\nnot-a-picture", ".png")

    def _picture(self, name):
        from PIL import Image
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (32,32), "#194652").save(path)
        return name

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow required")
    def test_research_import_preserves_external_provenance_and_stage(self):
        from harness_operations import upload_image
        source = self.project / self._picture("evidence/source.png")
        active = {"stage": "research-strategy", "agent": "01"}
        args = {"run_id": self.run.name, "extension": ".png",
                "data_base64": base64.b64encode(source.read_bytes()).decode("ascii")}
        state_before = (self.project / "status.json").read_bytes()
        with patch.object(mcp, "_project_and_stage", return_value=(self.run, active, self.project)):
            result = upload_image(mcp, args)
            with self.assertRaisesRegex(ValueError, "reference evidence"):
                upload_image(mcp, {**args, "asset_id": "IMG-001"})
        self.assertFalse(result["generation_observed"])
        self.assertEqual((self.project / result["path"]).read_bytes(), source.read_bytes())
        event = json.loads((self.run / "events.jsonl").read_text().splitlines()[-1])
        self.assertEqual(event["provenance"], "EXTERNAL_IMPORT")
        self.assertEqual(event["stage"], "research-strategy")
        self.assertEqual(state_before, (self.project / "status.json").read_bytes())

    def test_reference_import_still_rejects_definition_stage(self):
        from harness_operations import upload_image
        active = {"stage": "definition", "agent": "00"}
        with patch.object(mcp, "_project_and_stage", return_value=(self.run, active, self.project)):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                upload_image(mcp, {"run_id": self.run.name})

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow required")
    def test_fresh_review_uses_images_and_no_owner_conversation(self):
        images = [self._picture(f"evidence/board-{i}.png") for i in range(3)]
        direction = self.project / "creative-direction.md"
        text = direction.read_text(encoding="utf-8")
        heading = "## Direction divergence\n"
        rows = "| Direction ID | a | b | c | d | e | f | image |\n|---|---|---|---|---|---|---|---|\n"
        rows += "\n".join(f"| DIR-00{i+1} | a | b | c | d | e | f | {name} |" for i,name in enumerate(images))
        # Replace the section for a narrowly scoped provider protocol fixture.
        begin = text.index(heading)
        end = text.index("### Identity constraint fit", begin)
        direction.write_text(text[:begin]+heading+rows+"\n\n"+text[end:], encoding="utf-8")
        axes = ["composition","typography","color","media_integration","project_fit","reference_calibration","artistic_authority"]
        result = {"verdict":"PASS","summary":"Simulated reviewer, not an aesthetic claim", "selected_direction":"DIR-001", "findings":[],
                  "correction_kind":"NONE",
                  "axes":{axis:{"status":"PASS","evidence":images[0]+" versus "+images[1]+": fixture observation"} for axis in axes}}
        response = {"id":"simulated-response", "status":"completed", "output":[{"content":[{"type":"output_text","text":json.dumps(result)}]}]}
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_args): pass
            def read(self): return json.dumps(response).encode()
        stage = next(s for s in mcp.load_json(ROOT / "config/pipeline.json")["stages"] if s["id"] == "direction-review")
        with patch.dict(os.environ, {"OPENAI_API_KEY":"test-only", "AGENTIC_REVIEW_MODEL":"test-only"}), \
             patch("harness_review.benchmark_images", return_value=[images[1]]), \
             patch("urllib.request.urlopen", return_value=Response()) as call:
            run_visual_review(ROOT, self.project, stage, images)
        payload = json.loads(call.call_args.args[0].data)
        self.assertFalse(payload["store"])
        self.assertNotIn("previous_response_id", payload)
        self.assertNotIn("tools", payload)
        self.assertEqual(sum(part["type"] == "input_image" for part in payload["input"][0]["content"]), 3)
        self.assertEqual(review_record_errors(self.project,"direction-review"), [])
        direction.write_text(direction.read_text(encoding="utf-8")+"changed", encoding="utf-8")
        self.assertTrue(any("stale" in error for error in review_record_errors(self.project,"direction-review")))

    @unittest.skipUnless(os.getenv("AGENTIC_RUN_BROWSER_TESTS") == "1", "explicit local browser smoke test")
    def test_real_browser_captures_static_landing(self):
        from harness_render import render_static
        root = self.project / "implementation"
        root.mkdir(exist_ok=True)
        (root / "index.html").write_text('<!doctype html><meta name="viewport" content="width=device-width"><title>Runtime fixture</title><main data-scene-id="SCN-001"><h1>Runtime fixture, not a design benchmark</h1><button onclick="this.textContent=\'Clicked\'">Contact</button></main>', encoding="utf-8")
        (root / "assets").mkdir()
        (root / "assets/app.js").write_text("document.cookie='app=ok'; document.querySelector('h1').textContent += ' loaded-root-asset';", encoding="utf-8")
        with (root / "index.html").open("a", encoding="utf-8") as page:
            page.write('<script src="/assets/app.js"></script>')
        result = render_static(self.project, root, "index.html", ["SCN-001"], [{"type":"click","selector":"button"},{"type":"reduced-motion"}])
        self.assertEqual(len(result["captures"]), 8)
        observed = [capture["observed"] for capture in result["captures"] if capture["kind"] == "interaction"]
        self.assertTrue(all("Clicked" in capture["visibleText"] for capture in observed))
        self.assertTrue(all("loaded-root-asset" in capture["visibleText"] for capture in observed))
        self.assertTrue(all(capture["url"] == "/" for capture in observed))
        self.assertEqual(sum(capture["reducedMotion"] for capture in observed), 2)
        self.assertTrue(all((self.project / capture["file"]).is_file() for capture in result["captures"]))
        self.assertFalse(any(capture.get("errors") for capture in result["captures"]))


if __name__ == "__main__":
    unittest.main()
