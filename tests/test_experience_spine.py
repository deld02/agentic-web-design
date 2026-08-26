import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from project_validation import visual_narrative_review_errors  # noqa: E402
from validation_experience import experience_spine_errors  # noqa: E402


OUTLINE = """## Sitemap / page or section outline
| Scene ID | Section | User question / job | Available content and assets | Importance (`PRIMARY | UTILITY`) |
|---|---|---|---|---|
| SCN-001 | Hero | Why this? | Thesis and proof | PRIMARY |
| SCN-002 | Action | What next? | Scope and CTA | UTILITY |

## Experience spine
| Scene ID | Entry state | Active user question | Meaning to establish | Proof required | Desired shift | Next tension or action | Narrative function |
|---|---|---|---|---|---|---|---|
| SCN-001 | Comparing credible alternatives | Why is this relevant now? | The offer resolves a specific decision | A concrete thesis and evidence signal | From uncertainty to focused interest | Verify the method and its evidence | OPENING |
| SCN-002 | Interested and sufficiently informed | What is the sensible next step? | The next action is bounded and useful | Clear scope and direct CTA | From confidence to intentional action | Request the diagnostic or finish | ACTION |
"""


class ExperienceSpineTests(unittest.TestCase):
    def project(self, content=OUTLINE):
        temporary = tempfile.TemporaryDirectory()
        project = Path(temporary.name)
        (project / "content-architecture.md").write_text(content, encoding="utf-8")
        return temporary, project

    def test_complete_spine_covers_every_scene(self):
        temporary, project = self.project()
        try:
            self.assertEqual([], experience_spine_errors(project))
        finally:
            temporary.cleanup()

    def test_missing_scene_is_blocked(self):
        content = OUTLINE.replace("| SCN-002 | Interested and sufficiently informed", "| SCN-999 | Interested and sufficiently informed")
        temporary, project = self.project(content)
        try:
            errors = experience_spine_errors(project)
            self.assertTrue(any("missing scene SCN-002" in error for error in errors))
        finally:
            temporary.cleanup()

    def test_unknown_narrative_function_is_blocked(self):
        temporary, project = self.project(OUTLINE.replace("| OPENING |", "| ENGAGE |"))
        try:
            self.assertTrue(any("invalid narrative function" in error for error in experience_spine_errors(project)))
        finally:
            temporary.cleanup()

    def test_final_review_requires_experience_continuity(self):
        temporary, project = self.project()
        try:
            axes = ("WHOLE_PAGE_RHYTHM", "ASSET_NECESSITY", "FORMAT_FIT", "MECHANISM_ELIGIBILITY", "TRANSITION_CONTINUITY", "MOBILE_FALLBACK")
            rows = "\n".join(f"| {axis} | final desktop and mobile renders | no finding / 07 | PASS |" for axis in axes)
            qa = "## Visual and responsive verification\n\n### Visual narrative verification\n| Axis | Rendered evidence | Finding / correction owner | Verdict (`PASS | REVISE`) |\n|---|---|---|---|\n" + rows
            (project / "qa-release.md").write_text(qa, encoding="utf-8")
            self.assertIn("G4 visual narrative review missing EXPERIENCE_CONTINUITY", visual_narrative_review_errors(project))
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
