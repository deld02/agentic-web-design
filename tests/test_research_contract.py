"""Research packets and validators must agree on the bounded reference set."""
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from project_validation import reference_benchmark_errors
from stage_orchestrator import build_stage_packet


class ResearchContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)

    def write_references(self, hosts):
        roles = ["DIRECT", "SIMPLE", "FRONTIER", "SATURATED"]
        rows = ["### Live website benchmark", "| Website | Role | Discovery | Observation | Fit | Decision | URL | Checked | Capture |",
                "|---|---|---|---|---|---|---|---|---|"]
        for role, host in zip(roles, hosts):
            rows.append(f"| {host} | {role} | Search | Material detail | Good | Adapt | https://{host}/ | {date.today()} | evidence/ref.jpg |")
        (self.project / "research-strategy.md").write_text("\n".join(rows), encoding="utf-8")

    def test_three_websites_can_cover_multiple_lenses(self):
        self.write_references(["one.example", "one.example", "two.example", "three.example"])
        with patch("project_validation._physical_composition_error", return_value=None):
            self.assertEqual(reference_benchmark_errors(self.project), [])

    def test_duplicate_host_does_not_meet_minimum(self):
        self.write_references(["one.example", "www.one.example", "one.example", "one.example"])
        with patch("project_validation._physical_composition_error", return_value=None):
            self.assertTrue(any("requires 3" in e for e in reference_benchmark_errors(self.project)))

    def test_physical_evidence_still_required(self):
        self.write_references(["one.example", "one.example", "two.example", "three.example"])
        self.assertTrue(any("missing or invalid" in e for e in reference_benchmark_errors(self.project)))

    def test_packet_preserves_template_after_specialist_rewrites_artifact(self):
        (self.project / "research-strategy.md").write_text("# Research notes", encoding="utf-8")
        packet = build_stage_packet(ROOT, self.project,
                                    {"id": "research-strategy", "agent": "01", "mode": "research-strategy"},
                                    {"research-strategy.md"})
        template = packet["artifact_templates"]["research-strategy.md"]
        self.assertIn("### Live website benchmark", template)
        self.assertIn("MEMORY_STATUS", template)
        self.assertNotIn("creative-direction.md", packet["artifact_templates"])

    def test_unmodified_template_is_not_duplicated(self):
        text = (ROOT / "templates/project/research-strategy.md").read_text(encoding="utf-8")
        (self.project / "research-strategy.md").write_text(text, encoding="utf-8")
        packet = build_stage_packet(ROOT, self.project,
                                    {"id": "research-strategy", "agent": "01", "mode": "research-strategy"},
                                    {"research-strategy.md"})
        self.assertEqual(packet["artifact_templates"], {})


if __name__ == "__main__":
    unittest.main()
