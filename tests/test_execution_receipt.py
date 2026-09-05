import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validation_execution_receipt import execution_receipt_errors, write_execution_receipt  # noqa: E402


class ExecutionReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.run = Path(self.temp.name) / "managed-run"
        self.project = self.run / "project"
        self.site = self.project / "site"
        self.site.mkdir(parents=True)
        (self.site / "index.html").write_text("<main>Verified landing</main>", encoding="utf-8")
        pipeline = json.loads((ROOT / "config" / "pipeline.json").read_text(encoding="utf-8"))
        stages = pipeline["stages"]
        status = json.loads((ROOT / "templates" / "project" / "status.json").read_text(encoding="utf-8"))
        for gate in status["gates"].values():
            gate.update(status="APPROVED", evidence=["fixture"], blockers=[], last_decision="approved")
        for name in ("direction-review", "design-review", "build-review"):
            status["checkpoints"][name].update(status="APPROVED", review_context="ISOLATED", evidence=["fixture"], blockers=[], last_decision="approved")
        (self.project / "status.json").write_text(json.dumps(status), encoding="utf-8")
        (self.project / "project.config.json").write_text(json.dumps({"implementation_root": "site"}), encoding="utf-8")
        (self.project / "qa-release.md").write_text((ROOT / "templates" / "project" / "qa-release.md").read_text(encoding="utf-8"), encoding="utf-8")
        run = {"run_id": "managed-run", "execution_mode": "CHAT_INTERACTIVE", "status": "COMPLETE", "report_status": "PASS"}
        (self.run / "run.json").write_text(json.dumps(run), encoding="utf-8")
        (self.run / "report.json").write_text(json.dumps({"run_id": "managed-run", "status": "PASS", "findings": []}), encoding="utf-8")
        events = []
        for stage in stages:
            events.append({"event": "stage_start", "stage": stage["id"], "agent": stage["agent"]})
            if stage["id"] == "creative-master":
                events.append({"event": "tool_call", "stage": stage["id"], "agent": stage["agent"], "tool": "IMAGE_GEN"})
            events.append({"event": "stage_complete", "stage": stage["id"], "agent": stage["agent"]})
        (self.run / "events.jsonl").write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_managed_run_writes_verifiable_receipt(self):
        receipt = write_execution_receipt(self.run, ROOT)
        self.assertEqual([], execution_receipt_errors(receipt, ROOT))
        qa = (self.project / "qa-release.md").read_text(encoding="utf-8")
        self.assertIn("HARNESS_STATUS: COMPLETE", qa)
        self.assertIn("STAGES_COMPLETED: 13/13", qa)

    def test_incomplete_stage_sequence_cannot_create_receipt(self):
        lines = (self.run / "events.jsonl").read_text(encoding="utf-8").splitlines()
        (self.run / "events.jsonl").write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "every pipeline stage"):
            write_execution_receipt(self.run, ROOT)

    def test_changed_build_invalidates_receipt(self):
        receipt = write_execution_receipt(self.run, ROOT)
        (self.site / "index.html").write_text("<main>Changed after review</main>", encoding="utf-8")
        self.assertIn("implementation changed after execution receipt", execution_receipt_errors(receipt, ROOT))

    def test_tampered_receipt_is_rejected(self):
        receipt = write_execution_receipt(self.run, ROOT)
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data["validation_report"] = "FAIL"
        receipt.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("execution receipt content digest does not match", execution_receipt_errors(receipt, ROOT))

    def test_missing_master_generation_cannot_create_receipt(self):
        events = [json.loads(line) for line in (self.run / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        events = [item for item in events if item.get("event") != "tool_call"]
        (self.run / "events.jsonl").write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "artistic-master generation"):
            write_execution_receipt(self.run, ROOT)

    def test_unrelated_tool_call_is_not_image_generation(self):
        ledger = self.run / "events.jsonl"
        ledger.write_text(ledger.read_text(encoding="utf-8").replace("IMAGE_GEN", "READ_FILE"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "artistic-master generation"):
            write_execution_receipt(self.run, ROOT)


if __name__ == "__main__":
    unittest.main()
