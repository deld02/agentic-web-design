from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluation_harness import (  # noqa: E402
    advance_chat_run,
    append_event,
    chat_status,
    confirm_chat_image,
    create_packet,
    create_run,
    executor_doctor,
    event_findings,
    read_events,
    run_active,
    start_chat_run,
    validate_harness_config,
    visual_review_findings,
)
from validation_image_generation import missing_generation_receipts  # noqa: E402


class EvaluationHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.runs_root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def new_run(self) -> Path:
        return create_run("institutional-event", self.runs_root, "test-run")

    def record(self, run_dir: Path, event: str, stage: str, agent: str, **extra):
        return append_event(run_dir, {"event": event, "stage": stage, "agent": agent, **extra})

    def complete_until(self, run_dir: Path, last_stage: str, image_call: bool = True) -> None:
        pipeline = json.loads((ROOT / "config" / "pipeline.json").read_text(encoding="utf-8"))["stages"]
        for stage in pipeline:
            self.record(run_dir, "stage_start", stage["id"], stage["agent"])
            if stage["id"] == "creative-master" and image_call:
                self.record(run_dir, "tool_call", stage["id"], stage["agent"], tool="image_gen")
            self.record(run_dir, "stage_complete", stage["id"], stage["agent"])
            if stage["id"] == last_stage:
                break

    def test_init_creates_isolated_project_and_scenario(self):
        run_dir = self.new_run()
        self.assertTrue((run_dir / "project" / "status.json").is_file())
        self.assertIn("institutional-event", (run_dir / "project" / "brief.md").read_text(encoding="utf-8"))
        self.assertEqual(read_events(run_dir), [])

    def test_unknown_scenario_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown scenario"):
            create_run("not-real", self.runs_root, "bad")

    def test_wrong_owner_is_rejected_at_record_time(self):
        run_dir = self.new_run()
        with self.assertRaisesRegex(ValueError, "does not own"):
            self.record(run_dir, "stage_start", "creative-master", "04")

    def test_external_artifact_write_is_rejected(self):
        run_dir = self.new_run()
        with self.assertRaisesRegex(ValueError, "outside"):
            self.record(run_dir, "artifact_write", "definition", "00", target=str(self.runs_root.parent / "outside.md"))

    def test_skipping_pipeline_is_detected(self):
        run_dir = self.new_run()
        self.record(run_dir, "stage_start", "visual-experience", "04")
        codes = {item["code"] for item in event_findings(run_dir)}
        self.assertIn("PIPELINE_SKIP", codes)
        self.assertIn("MASTER_NOT_GENERATED", codes)

    def test_image_generation_order_is_accepted(self):
        run_dir = self.new_run()
        self.complete_until(run_dir, "visual-experience", image_call=True)
        codes = {item["code"] for item in event_findings(run_dir)}
        self.assertNotIn("MASTER_NOT_GENERATED", codes)
        self.assertNotIn("PIPELINE_ORDER", codes)

    def test_missing_image_generation_is_detected(self):
        run_dir = self.new_run()
        self.complete_until(run_dir, "visual-experience", image_call=False)
        codes = {item["code"] for item in event_findings(run_dir)}
        self.assertIn("MASTER_NOT_GENERATED", codes)

    def test_correction_budget_is_enforced(self):
        run_dir = self.new_run()
        self.record(run_dir, "stage_start", "definition", "00")
        self.record(run_dir, "correction", "definition", "00")
        self.record(run_dir, "correction", "definition", "00")
        codes = {item["code"] for item in event_findings(run_dir)}
        self.assertIn("CORRECTION_LIMIT", codes)

    def test_stage_timeout_is_detected(self):
        run_dir = self.new_run()
        self.record(run_dir, "stage_start", "definition", "00", at="2026-01-01T00:00:00Z")
        findings = event_findings(run_dir, now=datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc))
        self.assertIn("STAGE_TIMEOUT", {item["code"] for item in findings})

    def test_visual_review_requires_isolation_and_axis_evidence(self):
        run_dir = self.new_run()
        self.complete_until(run_dir, "build-review")
        findings = visual_review_findings(run_dir)
        codes = {item["code"] for item in findings}
        self.assertIn("REVIEW_ISOLATION", codes)
        self.assertIn("VISUAL_AXIS", codes)

    def test_packet_snapshots_artifacts_and_physical_evidence(self):
        run_dir = self.new_run()
        evidence = run_dir / "project" / "evidence"
        evidence.mkdir()
        (evidence / "desktop.png").write_bytes(b"physical-render")
        packet = create_packet(run_dir)
        manifest = json.loads((packet / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue((packet / "review.md").is_file())
        self.assertTrue(any(item["snapshot"].endswith("desktop.png") for item in manifest["files"]))

    def test_config_contract_rejects_duplicate_scenarios(self):
        config = json.loads((ROOT / "harness" / "scenarios.json").read_text(encoding="utf-8"))
        config["scenarios"].append(dict(config["scenarios"][0]))
        errors = validate_harness_config(config)
        self.assertTrue(any("duplicate scenario" in item for item in errors))

    def test_doctor_accepts_real_invocable_executor(self):
        report = executor_doctor([sys.executable, "--version"])
        self.assertEqual(report["status"], "READY")

    def test_active_runner_executes_and_validates_a_real_stage(self):
        run_dir = self.new_run()
        script = self.runs_root / "fixture_executor.py"
        script.write_text(
            r"""import json, os
from pathlib import Path
p=Path(os.environ['HARNESS_PROJECT_DIR'])
brief=p/'brief.md'; text=brief.read_text(encoding='utf-8')
text=text.replace('## Objective, audience and primary action\n', '## Objective, audience and primary action\n\nHelp local employers register for a factual public event.\n', 1)
text=text.replace('## Project type and provisional scope\n', '## Project type and provisional scope\n\nOne responsive event landing with registration as primary action.\n', 1)
brief.write_text(text,encoding='utf-8')
status=json.loads((p/'status.json').read_text(encoding='utf-8'))
status['gates']['G0'].update(status='APPROVED',evidence=['brief.md'],blockers=[],last_decision='fixture definition approved')
status['checkpoints']['research-strategy']['status']='ACTIVE'
status.update(active_stage='research-strategy',active_gate=None,active_agent='01',active_mode='research-strategy',status='ACTIVE')
status['release']={'eligible':False,'reason':'G1 pending'}
(p/'status.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
""",
            encoding="utf-8",
        )
        result = run_active(run_dir, [sys.executable, str(script)], until="definition")
        self.assertEqual(result["status"], "PARTIAL", result)
        events = read_events(run_dir)
        self.assertTrue(any(item["event"] == "stage_complete" and item["stage"] == "definition" for item in events))
        self.assertTrue(any(item["event"] == "artifact_write" and item["target"] == "brief.md" for item in events))

    def test_active_runner_fails_clearly_when_executor_cannot_start(self):
        run_dir = self.new_run()
        result = run_active(run_dir, ["executor-that-does-not-exist"], until="definition")
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("executor could not start", " ".join(result["findings"]))

    def test_chat_start_opens_exactly_definition_without_external_cli(self):
        result = start_chat_run("institutional-event", self.runs_root, "chat-run")
        self.assertEqual(result["execution_mode"], "CHAT_INTERACTIVE")
        self.assertEqual(result["stage"], "definition")
        self.assertEqual(chat_status(Path(result["run_dir"]))["agent"], "00")

    def test_chat_start_accepts_a_real_custom_brief(self):
        result = start_chat_run(None, self.runs_root, "custom-chat", "Create a distinctive landing for a local craft workshop.")
        run_dir = Path(result["run_dir"])
        self.assertEqual(result["stage"], "definition")
        self.assertIn("local craft workshop", (run_dir / "project" / "brief.md").read_text(encoding="utf-8"))

    def test_chat_next_validates_before_opening_the_next_stage(self):
        result = start_chat_run("institutional-event", self.runs_root, "chat-run")
        advanced = advance_chat_run(Path(result["run_dir"]))
        self.assertEqual(advanced["status"], "REVISE")
        self.assertEqual(advanced["stage"], "definition")
        self.assertTrue(advanced["findings"])

    def test_chat_image_requires_creative_master_and_physical_raster(self):
        result = start_chat_run("institutional-event", self.runs_root, "chat-run")
        run_dir = Path(result["run_dir"])
        image = run_dir / "project" / "evidence" / "master.png"
        image.parent.mkdir()
        image.write_bytes(b"\x89PNG\r\n\x1a\n")
        with self.assertRaisesRegex(ValueError, "creative-master"):
            confirm_chat_image(run_dir, image)

    def test_chat_image_records_declared_production_asset(self):
        run_dir = self.new_run()
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8")); run.update(execution_mode="CHAT_INTERACTIVE", status="RUNNING")
        (run_dir / "run.json").write_text(json.dumps(run), encoding="utf-8")
        self.complete_until(run_dir, "technology-selection")
        self.record(run_dir, "stage_start", "production-plan", "05")
        project = run_dir / "project"
        config = json.loads((project / "project.config.json").read_text(encoding="utf-8"))
        config["implementation_root"] = "site"
        (project / "project.config.json").write_text(json.dumps(config), encoding="utf-8")
        plan = project / "production-plan.md"
        marker = "| ID | Scene + observed render need | Production type + representation/truth class | Payload role / selected method | Status | Final file / fallback | External loop handoff (`IH-*`) + production brief | Exact integration in landing |\n|---|---|---|---|---|---|---|---|"
        text = plan.read_text(encoding="utf-8").replace(
            marker, marker + "\n| IMG-001 | SCN-001 hero | SCENE_PLATE / CONCEPTUAL | PRIMARY:EXTERNAL_IMAGE_LOOP | RETURNED | assets/hero.webp | IH-001 generated hero | hero background |",
        )
        plan.write_text(text, encoding="utf-8")
        image = project / "site" / "assets" / "hero.webp"
        image.parent.mkdir(parents=True)
        image.write_bytes(b"RIFFxxxxWEBPgenerated")
        self.assertEqual(missing_generation_receipts(project, read_events(run_dir), {"CHATGPT_IMAGE"}), ["IMG-001"])
        result = confirm_chat_image(run_dir, image, "IMG-001")
        self.assertEqual(result["stage"], "production-plan")
        self.assertTrue(any(item.get("target") == "IMG-001" for item in read_events(run_dir)))
        self.assertEqual(missing_generation_receipts(project, read_events(run_dir), {"CHATGPT_IMAGE"}), [])

    def test_chat_image_rejects_undeclared_production_asset(self):
        run_dir = self.new_run()
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8")); run.update(execution_mode="CHAT_INTERACTIVE", status="RUNNING")
        (run_dir / "run.json").write_text(json.dumps(run), encoding="utf-8")
        self.complete_until(run_dir, "technology-selection")
        self.record(run_dir, "stage_start", "production-plan", "05")
        with self.assertRaisesRegex(ValueError, "declared generated"):
            confirm_chat_image(run_dir, run_dir / "project" / "site" / "hero.png", "IMG-999")


if __name__ == "__main__":
    unittest.main()
