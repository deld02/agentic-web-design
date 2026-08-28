import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validation_release_integrity import implementation_digest  # noqa: E402
from validation_spatial_experience import (  # noqa: E402
    spatial_plan_errors,
    spatial_qa_errors,
    spatial_selection_errors,
    spatial_stage_instruction,
    spatial_technology_errors,
)


PNG = b"\x89PNG\r\n\x1a\nspatial-evidence"


class SpatialExperienceTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        project = Path(temporary.name) / "project"
        implementation = Path(temporary.name) / "site"
        project.mkdir(); implementation.mkdir()
        (implementation / "index.html").write_text("<main data-spatial>Spatial scene</main>", encoding="utf-8")
        (project / "content-architecture.md").write_text(
            "# Content\n\n## Sitemap / page or section outline\n\n"
            "| Scene ID | Purpose | Content | CTA | Notes |\n|---|---|---|---|---|\n"
            "| SCN-001 | explain material change | real process | explore | anchor |\n",
            encoding="utf-8",
        )
        return temporary, project, implementation

    def write_selection(self, project, mode="INTERACTIVE_3D", review="PASS"):
        evidence = project / "evidence" / "spatial-review.png"
        evidence.parent.mkdir(exist_ok=True); evidence.write_bytes(PNG)
        candidates = ["FLAT_2D", "LAYERED_2D", "RENDERED_3D"]
        if mode == "INTERACTIVE_3D":
            candidates.append("INTERACTIVE_3D")
        rows = "\n".join(
            f"| {candidate} | explain the same material transformation | observable comparison for this scene | viewpoint and manipulation are tested | bounded mobile and performance cost | static fallback preserves the primary action | {'SELECTED' if candidate == mode else 'REJECTED'} |"
            for candidate in candidates
        )
        (project / "visual-system.md").write_text(
            "# Visual\n\n### Spatial modality decision (conditional)\n\n"
            f"SPATIAL_MODE: {mode}\nSELECTED_SCENE_IDS: SCN-001\n"
            "WHY_SIMPLER_FAILS: viewpoint reveals the material transformation unavailable in a fixed composition\n"
            f"SPATIAL_REVIEW: {review}\nSPATIAL_REVIEW_EVIDENCE: evidence/spatial-review.png\n\n"
            "| Candidate mode | Same narrative job | Observable gain | Interaction / viewpoint necessity | Mobile and performance cost | Fallback equivalence | Verdict (`SELECTED | REJECTED`) |\n"
            "|---|---|---|---|---|---|---|\n" + rows + "\n",
            encoding="utf-8",
        )

    def write_technology(self, project, with_spike=True):
        if with_spike:
            (project / "evidence" / "spike.png").write_bytes(PNG)
        (project / "technology-decision.md").write_text(
            "# Technology\n\n## Options compared\n\n"
            "| Option | Fit | Costs / risks | Why keep or reject |\n|---|---|---|---|\n"
            "| model-viewer | contained real model | limited choreography | simplest option tested |\n"
            "| Three.js | semantic camera states | runtime budget | selected after spike |\n\n"
            "## Spike evidence when needed\n\n### Spatial runtime decision (conditional)\n\n"
            "SPATIAL_RUNTIME_SELECTION: Three.js with a contained canvas\n"
            "SIMPLEST_SPATIAL_OPTION_TESTED: model-viewer contained model\n"
            f"SPATIAL_SPIKE_EVIDENCE: {'evidence/spike.png' if with_spike else ''}\n"
            "SPATIAL_KILL_CRITERION: use rendered sequence if mobile state loses legibility\n",
            encoding="utf-8",
        )

    def write_plan(self, project):
        (project / "production-plan.md").write_text(
            "# Plan\n\n### Spatial experience contract (conditional)\n\n"
            "ASSET_BUDGET: one compressed GLB under the measured project ceiling\n"
            "RUNTIME_BUDGET: one isolated canvas with lazy runtime loading\n"
            "LOADING_STRATEGY: poster first and runtime after meaningful intent\n"
            "LOW_POWER_POLICY: preserve poster and HTML explanation without WebGL\n"
            "FAILURE_FALLBACK: replace canvas with approved poster and keep CTA\n\n"
            "| State ID | Scene ID | Narrative state / job | Trigger / input | Camera | Object / material / light | HTML / copy relationship | Transition onward | Mobile / reduced-motion / failure fallback | Evidence target |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            "| SPT-001 | SCN-001 | reveal material transformation clearly | enter the process scene | approach the material sample slowly | layered sample with warm directional light | HTML explanation remains beside the object | settle into the transformed state | approved poster keeps the same explanation | desktop and mobile state capture |\n",
            encoding="utf-8",
        )

    def write_qa(self, project, implementation):
        axes = [
            "SPATIAL_DIRECTION_FIDELITY", "HTML_LEGIBILITY", "MATERIAL_LIGHTING_COHERENCE",
            "ASSET_INTEGRITY", "FALLBACK_EQUIVALENCE", "CAMERA_CONTINUITY",
            "OBJECT_INTERSECTIONS", "RUNTIME_SMOOTHNESS",
        ]
        axis_rows = "\n".join(f"| {axis} | desktop and mobile rendered state evidence | no blocking finding / 07 | PASS |" for axis in axes)
        digest = implementation_digest(implementation)
        evidence = project / "evidence"
        (evidence / "state-desktop.png").write_bytes(PNG)
        (evidence / "state-mobile.png").write_bytes(PNG)
        traversal = (
            f"| SPT-001 | SCN-001 | DESKTOP | enter the process scene | camera reveals transformed material beside HTML | observed state matches approved storyboard | evidence/state-desktop.png | PASS | sha256:{digest} |\n"
            f"| SPT-001 | SCN-001 | MOBILE | enter through touch scroll | static camera preserves object and HTML hierarchy | observed mobile fallback remains equivalent | evidence/state-mobile.png | PASS | sha256:{digest} |"
        )
        (project / "qa-release.md").write_text(
            "# QA\n\n### Spatial QA (conditional)\n\n"
            "| Axis | Rendered/runtime evidence | Finding / correction owner | Verdict (`PASS | REVISE`) |\n|---|---|---|---|\n"
            + axis_rows + "\n\n### Spatial state traversal (conditional)\n\n"
            "| State ID | Scene ID | Viewport (`DESKTOP | MOBILE`) | Trigger / input | Expected camera/object/HTML state | Observed result | Physical evidence relative to project | Verdict (`PASS | REVISE`) | Source digest |\n"
            "|---|---|---|---|---|---|---|---|---|\n" + traversal + "\n",
            encoding="utf-8",
        )

    def test_untouched_conditional_template_does_not_activate_spatial_contract(self):
        temporary, project, _implementation = self.fixture()
        try:
            (project / "visual-system.md").write_text((ROOT / "templates/project/visual-system.md").read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual([], spatial_selection_errors(project))
        finally:
            temporary.cleanup()

    def test_interactive_selection_requires_all_comparisons_and_review(self):
        temporary, project, _implementation = self.fixture()
        try:
            self.write_selection(project, review="REVISE")
            text = (project / "visual-system.md").read_text(encoding="utf-8").replace("| RENDERED_3D | explain", "| OMITTED | explain")
            (project / "visual-system.md").write_text(text, encoding="utf-8")
            errors = spatial_selection_errors(project)
            self.assertTrue(any("missing RENDERED_3D" in error for error in errors))
            self.assertTrue(any("SPATIAL_REVIEW PASS" in error for error in errors))
        finally:
            temporary.cleanup()

    def test_complete_interactive_contract_passes_all_spatial_layers(self):
        temporary, project, implementation = self.fixture()
        try:
            self.write_selection(project); self.write_technology(project); self.write_plan(project); self.write_qa(project, implementation)
            self.assertEqual([], spatial_selection_errors(project))
            self.assertEqual([], spatial_technology_errors(project))
            self.assertEqual([], spatial_plan_errors(project))
            self.assertEqual([], spatial_qa_errors(project, implementation))
        finally:
            temporary.cleanup()

    def test_interactive_runtime_needs_physical_bounded_spike(self):
        temporary, project, _implementation = self.fixture()
        try:
            self.write_selection(project); self.write_technology(project, with_spike=False)
            self.assertTrue(any("physical SPATIAL_SPIKE_EVIDENCE" in error for error in spatial_technology_errors(project)))
        finally:
            temporary.cleanup()

    def test_harness_routes_without_making_executor_a_runtime(self):
        temporary, project, _implementation = self.fixture()
        try:
            self.write_selection(project)
            instruction = spatial_stage_instruction(project, "technology-selection")
            self.assertIn("INTERACTIVE_3D", instruction)
            self.assertNotIn("Antigravity", instruction)
        finally:
            temporary.cleanup()

    def test_spatial_decisions_have_one_project_artifact_authority_each(self):
        expected = {
            "### Spatial modality decision (conditional)": "visual-system.md",
            "### Spatial runtime decision (conditional)": "technology-decision.md",
            "### Spatial experience contract (conditional)": "production-plan.md",
            "### 3D production provenance": "production-plan.md",
            "### Spatial QA (conditional)": "qa-release.md",
            "### Spatial state traversal (conditional)": "qa-release.md",
        }
        templates = list((ROOT / "templates/project").glob("*.md"))
        for heading, owner in expected.items():
            occurrences = [path.name for path in templates if heading in path.read_text(encoding="utf-8")]
            self.assertEqual([owner], occurrences, heading)


if __name__ == "__main__":
    unittest.main()
