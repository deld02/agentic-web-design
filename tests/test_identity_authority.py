import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validation_identity import (  # noqa: E402
    identity_authority_errors,
    identity_direction_trace_errors,
    identity_visual_trace_errors,
)


RESEARCH = """# Research
## Identity authority contract
IDENTITY_STATUS: EVALUATED
| Identity ID | Element / source | Current evidence and role | Authority (`BINDING | EVOLVE_WITHIN_LIMITS | OPEN_TO_REPLACE`) | Objective fit | Allowed change | Forbidden consequence | Downstream owner |
|---|---|---|---|---|---|---|---|
| IDN-001 | Logo and red | Recognition | BINDING | Strong | Neutral range | Losing red dominance | 03 / 04 |
"""

CREATIVE = """# Creative
## Direction divergence
| Direction ID | Concept / perception | Typography | Composition | Media / materiality | Depth / motion | Human presence / metaphor | Physical board relative to project |
|---|---|---|---|---|---|---|---|
| DIR-001 | A | A | A | A | A | A | a.png |
| DIR-002 | B | B | B | B | B | B | b.png |
| DIR-003 | C | C | C | C | C | C | c.png |
### Identity constraint fit
| Direction ID | Identity IDs addressed | Preserve / evolve / replace response | Observable evidence and risk | Verdict (`PASS | FAIL`) |
|---|---|---|---|---|
| DIR-001 | IDN-001 | Preserve | Visible | PASS |
| DIR-002 | IDN-001 | Preserve | Visible | PASS |
| DIR-003 | IDN-001 | Preserve | Visible | PASS |
## Creative master handoff
IDENTITY_INHERITANCE: IDN-001
"""

VISUAL = """# Visual
## Creative master development
IDENTITY_INHERITANCE: IDN-001
### Independent color challenge
| Physical evidence (`CLR-ID:path`) | Accent removed | Neutral swap | Category-typical swap | Identity constraints tested (`IDN-* | NO_EXISTING_IDENTITY`) | Recognition / brand-drift finding | Observable advantage of selected territory | Verdict (`PASS | BRAND_DRIFT | REVISE`) |
|---|---|---|---|---|---|---|---|
| CLR-900:sheet.png | weaker | flatter | generic | IDN-001 | recognition preserved | clearer hierarchy | PASS |
"""


class IdentityAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        (self.project / "project.config.json").write_text(
            json.dumps({"visual_identity_mode": "evolve"}), encoding="utf-8"
        )
        (self.project / "research-strategy.md").write_text(RESEARCH, encoding="utf-8")
        (self.project / "creative-direction.md").write_text(CREATIVE, encoding="utf-8")
        (self.project / "visual-system.md").write_text(VISUAL, encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_identity_is_traced_across_gates(self):
        self.assertEqual([], identity_authority_errors(self.project))
        self.assertEqual([], identity_direction_trace_errors(self.project))
        self.assertEqual([], identity_visual_trace_errors(self.project))

    def test_direction_cannot_drop_identity_reference(self):
        path = self.project / "creative-direction.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| DIR-002 | IDN-001", "| DIR-002 | NONE"), encoding="utf-8")
        self.assertIn("G2 DIR-002 must address every G1 identity ID", identity_direction_trace_errors(self.project))

    def test_brand_drift_blocks_g3(self):
        path = self.project / "visual-system.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| PASS |", "| BRAND_DRIFT |"), encoding="utf-8")
        self.assertIn("G3 independent color challenge detected BRAND_DRIFT", identity_visual_trace_errors(self.project))

    def test_no_identity_is_incompatible_with_inherit_mode(self):
        path = self.project / "research-strategy.md"
        path.write_text("# Research\n## Identity authority contract\nIDENTITY_STATUS: NO_EXISTING_IDENTITY\n", encoding="utf-8")
        self.assertIn("G1 inherit/evolve identity mode requires evaluated identity evidence", identity_authority_errors(self.project))


if __name__ == "__main__":
    unittest.main()
