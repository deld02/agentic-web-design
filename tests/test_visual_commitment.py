import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validation_motion_payload import motion_payload_errors
from validation_user_authority import explicit_static_only_authorized, explicit_text_only_authorized


class VisualCommitmentTests(unittest.TestCase):
    def fixture(self, immutable_brief, text_quote="", static_quote=""):
        td = tempfile.TemporaryDirectory()
        run = Path(td.name) / "run"
        project = run / "project"
        project.mkdir(parents=True)
        (run / "scenario.json").write_text(json.dumps({"brief": immutable_brief}), encoding="utf-8")
        markers = (
            f"USER_EXPLICIT_TEXT_ONLY: {text_quote}\n"
            f"USER_EXPLICIT_STATIC_ONLY: {static_quote}\n"
        )
        (project / "brief.md").write_text(markers, encoding="utf-8")
        (project / "production-plan.md").write_text(markers, encoding="utf-8")
        return td, project

    def test_provider_rejection_does_not_authorize_text_only(self):
        td, project = self.fixture("No uses Magnific para las imágenes", "No uses Magnific para las imágenes")
        try:
            self.assertFalse(explicit_text_only_authorized(project))
        finally:
            td.cleanup()

    def test_agent_cannot_invent_text_only_authority(self):
        td, project = self.fixture("Crea una landing visual premium", "Quiero una landing solo texto")
        try:
            self.assertFalse(explicit_text_only_authorized(project))
        finally:
            td.cleanup()

    def test_exact_global_text_only_request_is_authorized(self):
        quote = "Quiero una landing solo texto, sin imágenes"
        td, project = self.fixture(quote, quote)
        try:
            self.assertTrue(explicit_text_only_authorized(project))
        finally:
            td.cleanup()

    def test_exact_static_request_is_authorized(self):
        quote = "Quiero una web sin animaciones"
        td, project = self.fixture(quote, static_quote=quote)
        try:
            self.assertTrue(explicit_static_only_authorized(project))
        finally:
            td.cleanup()

    def test_static_winner_cannot_waive_whole_landing(self):
        td, project = self.fixture("Crea una landing premium")
        try:
            plan = (project / "production-plan.md").read_text(encoding="utf-8")
            plan += (
                "\n## Page visual narrative map\n\n"
                "| Scene ID | Page beat | Visual job | Intensity | Selected format | Selected behavior | Trigger | Decomposition | Fallback | Transition |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| SCN-001 | ANCHOR | Lead | high | BACKGROUND | STATIC | resolved composition | one plate | same | next |\n"
                "\n### Material effect decisions\n\n"
                "| Effect ID / scene | Opportunity | Static | Simple | Expressive | Sources | Winner | Prototype | Fallback | Status | Proof |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| FX-001 / hero | defining | still | reveal | assembly | lab | static | render | same | STATIC_WINNER_REVIEWED | STATIC:render |\n"
            )
            (project / "production-plan.md").write_text(plan, encoding="utf-8")
            errors = motion_payload_errors(project)
            self.assertTrue(any("non-static" in error for error in errors))
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
