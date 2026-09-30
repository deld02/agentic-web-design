"""Recorded decisions and provenance, not artistic taste certification."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from validation_creative_decisions import evidence_led, source_errors, plan_errors, critical_media_errors, generation_required
from harness_design_plan import seal_plan
from project_validation import artistic_master_errors, color_direction_errors
from harness_review import review_axes
from validate_delivery import validate_delivery
ROOT=Path(__file__).resolve().parents[1]

class EvidenceLedTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.run=Path(tmp.name);self.p=self.run/'project';self.p.mkdir()
        self.write('project.config.json','{"design_contract":"evidence-led-v2"}')
        self.write('content-architecture.md','## Sitemap / page or section outline\n| Scene ID | Section |\n|---|---|\n| SCN-001 | Hero |\n')
        self.write('research-strategy.md','## Discovered evidence authority\n| Source ID | Type | Source | Finding | Truth | Evidence | Date | Relevance |\n|---|---|---|---|---|---|---|---|\n| SRC-001 | WEB | https://example.com | Personal offer | VERIFIED | https://example.com | 2026-10-01 | Trust |\n')
        bar=''.join(f'{k}: Actual legible relationship\n' for k in ['PREMIUM_MEANS_HERE','CATEGORY_BASELINE_TO_EXCEED','MUST_BE_AUTHORED','MUST_AVOID','MASTER_MUST_PROVE','LANDING_MUST_PRESERVE'])
        self.write('creative-direction.md','## Project-specific quality bar\n'+bar+'## Creative idea\nCREATIVE_IDEA: Subject establishes trust\nPROJECT_SOURCE_IDS: SRC-001\nWHY_THIS_PROJECT: Direct service\nOBSERVABLE_CONSEQUENCE: Evidence leads\n## Direction divergence\n| Direction ID | Concept |\n|---|---|\n## Artistic master\n')
        self.write('visual-system.md','## Global page rhythm\nRHYTHM_SEQUENCE: SCN-001 opening\nPEAKS_AND_RESTS: pause\nREPETITION_CONTROL: one subject\nHERO_TO_BODY_CONTINUITY: purpose\n### Section design loop\n| Scene | Attempt |\n|---|---|\n## Foundation alternatives and decision evidence\n')
    def write(self,name,text): (self.p/name).write_text(text,encoding='utf-8')
    def append(self,name,text): self.write(name,(self.p/name).read_text(encoding='utf-8')+text)
    def image(self,name): Image.new('RGB',(32,32)).save(self.p/name)

    def test_source_has_locator_and_valid_date(self):
        self.assertEqual([],source_errors(self.p))
        self.write('research-strategy.md',(self.p/'research-strategy.md').read_text().replace('https://example.com | 2026-10-01','missing.png | 2026-99-99'))
        self.assertEqual(2,len(source_errors(self.p)))

    def test_managed_proof_source_is_writable_only_in_v2(self):
        import harness_mcp_server as mcp
        target = mcp._write_allowed(self.p, 'creative-master', 'evidence/proof/index.html')
        self.assertEqual(self.p / 'evidence/proof/index.html', target)
        self.write('project.config.json', '{}')
        with self.assertRaises(ValueError):
            mcp._write_allowed(self.p, 'creative-master', 'evidence/proof/index.html')

    def test_contract_cannot_be_downgraded(self):
        (self.run/'run.json').write_text('{"design_contract":"evidence-led-v2"}')
        self.write('project.config.json','{}');self.assertTrue(evidence_led(self.p))

    def test_seal_change_invalidates_permission(self):
        self.assertTrue(plan_errors(self.p,'direction-divergence'))
        seal_plan(self.run,'direction-divergence')
        self.assertEqual([],plan_errors(self.p,'direction-divergence'))
        self.write('creative-direction.md',(self.p/'creative-direction.md').read_text().replace('Subject establishes','Another subject establishes'))
        self.assertTrue(plan_errors(self.p,'direction-divergence'))

    def test_detail_cannot_precede_macro_lock(self):
        self.append('visual-system.md','| Candidate system | Detail |\n|---|---|\n| chosen | already designed |\n')
        with self.assertRaisesRegex(ValueError,'foundation'):seal_plan(self.run,'visual-experience')

    def test_typographic_proof_requires_capture_not_generation(self):
        self.image('study.png');self.write('study.html','<h1>Type study</h1>')
        self.append('creative-direction.md','ARTISTIC_MASTER: AM-001\nSOURCE_DIRECTION: DIR-001\nPROOF_MODE: TYPOGRAPHIC_STUDY\nPROOF_SOURCE: study.html\nARTISTIC_INTENT: Hierarchy\nPROJECT_GROUNDS: Person\nWEB_TRANSLATION_BOUNDARY: Capture never ships\n| Evidence ID | Question | Method | File |\n|---|---|---|---|\n| AM-001 | hierarchy | TYPOGRAPHIC_STUDY | study.png |\n## Direction selection handoff\nSELECTED_DIRECTION: DIR-001\n')
        self.assertFalse(generation_required(self.p));self.assertEqual([],artistic_master_errors(self.p))
        self.write('creative-direction.md',(self.p/'creative-direction.md').read_text().replace('TYPOGRAPHIC_STUDY','GENERATED_IMAGE'))
        self.assertTrue(generation_required(self.p));self.assertTrue(artistic_master_errors(self.p))

    def test_critical_media_requires_physical_proof(self):
        self.append('visual-system.md','### Composition-critical media\n| Scene ID | Decision | Reason | Evidence | Boundary |\n|---|---|---|---|---|\n| SCN-001 | CRITICAL | Defines crop | missing.png | identity/crop |\n')
        self.assertTrue(critical_media_errors(self.p));self.image('missing.png')
        self.assertEqual([],critical_media_errors(self.p))

    def test_color_uncertainty_changes_evidence_requirement(self):
        self.image('color.png')
        self.append('visual-system.md','### Color direction territories\nCOLOR_UNCERTAINTY: LOW\nCOLOR_REASON: Binding identity\n| Territory | Evidence | Hierarchy | Provenance | Composition | Accessibility | Verdict |\n|---|---|---|---|---|---|---|\n| BRAND_LED | CLR-001:color.png | White field black text | Identity | Large surface | Contrast checked | SELECTED |\n')
        self.assertEqual([],color_direction_errors(self.p))
        self.write('visual-system.md',(self.p/'visual-system.md').read_text().replace('LOW','MATERIAL'))
        self.assertTrue(color_direction_errors(self.p))

    def test_axes_versioning(self):
        self.assertIn('conceptual_distance',review_axes(ROOT,self.p,'direction-review'))
        self.assertIn('macro_rhythm',review_axes(ROOT,self.p,'design-review'))
        self.write('project.config.json','{}')
        self.assertNotIn('macro_rhythm',review_axes(ROOT,self.p,'design-review'))

    def test_native_design_has_no_image_quota(self):
        root=self.p/'implementation';root.mkdir();(root/'index.html').write_text('<h1>Native composition</h1>')
        self.write('production-plan.md','## Asset inventory and readiness\n')
        with patch('validation_blender.blender_delivery_errors',return_value=[]):errors,_=validate_delivery(self.p,root)
        self.assertFalse(any('no FINAL IMG' in e for e in errors))
        self.write('project.config.json','{}')
        with patch('validation_blender.blender_delivery_errors',return_value=[]):errors,_=validate_delivery(self.p,root)
        self.assertTrue(any('no FINAL IMG' in e for e in errors))
