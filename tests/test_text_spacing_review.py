import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from project_validation import visual_narrative_review_errors


AXES = (
    "WHOLE_PAGE_RHYTHM", "HERO_TARGET_FIDELITY", "EXPERIENCE_CONTINUITY", "ASSET_NECESSITY",
    "FORMAT_FIT", "FOCAL_VISUAL_AUTHORITY", "MECHANISM_ELIGIBILITY", "TRANSITION_CONTINUITY", "MOBILE_FALLBACK", "TEXT_SPACING_CRAFT",
)


class TextSpacingReviewTests(unittest.TestCase):
    def fixture(self, capability="jakub-interface-polish", mode="FULL", spacing_evidence=None):
        td = tempfile.TemporaryDirectory()
        project = Path(td.name) / "project"
        project.mkdir()
        spacing_evidence = spacing_evidence or "SCN-001 and SCN-002 inspected in final desktop and mobile renders"
        rows = []
        for axis in AXES:
            if axis == "HERO_TARGET_FIDELITY":
                evidence = "CMP-001 compared with final desktop and mobile renders"
            elif axis == "TEXT_SPACING_CRAFT":
                evidence = spacing_evidence
            elif axis == "FOCAL_VISUAL_AUTHORITY":
                evidence = "SCN-001 removal and produced alternative compared in final desktop and mobile renders"
            else:
                evidence = "final desktop and mobile rendered evidence"
            rows.append(f"| {axis} | {evidence} | no finding / 07 | PASS |")
        qa = (
            "# QA\n\n## Visual and responsive verification\n\n"
            f"FINAL_TEXT_SPACING_CAPABILITY: {capability}\n"
            f"FINAL_TEXT_SPACING_MODE: {mode}\n\n"
            "### Visual narrative verification\n\n"
            "| Axis | Rendered evidence | Finding / correction owner | Verdict (`PASS | REVISE`) |\n"
            "|---|---|---|---|\n" + "\n".join(rows) + "\n"
        )
        (project / "qa-release.md").write_text(qa, encoding="utf-8")
        return td, project

    def test_full_final_polish_passes_with_scene_and_viewport_evidence(self):
        td, project = self.fixture()
        try:
            self.assertEqual(visual_narrative_review_errors(project), [])
        finally:
            td.cleanup()

    def test_missing_full_polish_capability_is_blocked(self):
        td, project = self.fixture(capability="")
        try:
            self.assertTrue(any("jakub-interface-polish" in item for item in visual_narrative_review_errors(project)))
        finally:
            td.cleanup()

    def test_generic_spacing_claim_without_scenes_and_viewports_is_blocked(self):
        td, project = self.fixture(spacing_evidence="Spacing looks correct")
        try:
            self.assertTrue(any("TEXT_SPACING_CRAFT evidence" in item for item in visual_narrative_review_errors(project)))
        finally:
            td.cleanup()

    def test_focal_visual_without_physical_alternative_comparison_is_blocked(self):
        td, project = self.fixture()
        try:
            qa = project / "qa-release.md"
            qa.write_text(
                qa.read_text(encoding="utf-8").replace(
                    "SCN-001 removal and produced alternative compared in final desktop and mobile renders",
                    "The decorative circles look acceptable",
                ),
                encoding="utf-8",
            )
            self.assertTrue(any("FOCAL_VISUAL_AUTHORITY" in item for item in visual_narrative_review_errors(project)))
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
