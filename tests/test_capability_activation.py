import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validation_capability_activation import stage_activation_errors, stage_capability_instruction


def artifact(rows, narrative=""):
    return (
        narrative + "\n## Design capability log\n\n"
        "| Capability | Mode | Reason | Findings | Result |\n"
        "|---|---|---|---|---|\n" +
        "\n".join(f"| {capability} | {mode} | required | applied | PASS |" for capability, mode in rows) + "\n"
    )


class CapabilityActivationTests(unittest.TestCase):
    def test_stage_prompt_routes_required_core_capabilities(self):
        instruction = stage_capability_instruction(ROOT, "direction-divergence")
        self.assertIn("web-design-capabilities", instruction)
        self.assertIn("anthropic-frontend-design", instruction)
        self.assertIn("taste-direction-challenger", instruction)

    def test_missing_automatic_capability_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "creative-direction.md").write_text(artifact([]), encoding="utf-8")
            errors = stage_activation_errors(project, ROOT, "direction-divergence")
            self.assertTrue(any("anthropic-frontend-design" in item for item in errors))
            self.assertTrue(any("taste-direction-challenger" in item for item in errors))

    def test_logged_core_capabilities_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            rows = (("anthropic-frontend-design", "direction-divergence"), ("taste-direction-challenger", "direction-divergence"))
            (project / "creative-direction.md").write_text(artifact(rows), encoding="utf-8")
            self.assertEqual(stage_activation_errors(project, ROOT, "direction-divergence"), [])

    def test_material_motion_requires_emil(self):
        narrative = (
            "## Page visual narrative map\n\n"
            "| Scene ID | Beat | Job | Intensity | Format | Behavior | Trigger | Layers | Fallback | Transition |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            "| SCN-001 | ANCHOR | thesis | high | BACKGROUND | PARALLAX | depth | layers | static | next |\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "production-plan.md").write_text(artifact([], narrative), encoding="utf-8")
            errors = stage_activation_errors(project, ROOT, "production-plan")
            self.assertTrue(any("emil-motion-craft" in item for item in errors))

    def test_classified_flat_result_requires_impeccable(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            rows = (("jakub-interface-polish", "build-review"), ("vercel-web-interface-guidelines", "build-review"))
            text = artifact(rows) + "\n## Findings\n\nClassification: FLAT\n"
            (project / "qa-release.md").write_text(text, encoding="utf-8")
            errors = stage_activation_errors(project, ROOT, "build-review")
            self.assertTrue(any("impeccable-craft-correction" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
