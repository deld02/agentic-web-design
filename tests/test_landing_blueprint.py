import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validation_landing_blueprint import blueprint_errors, design_approval_errors, record_design_approval
from harness_review import _snapshot
from project_validation import creative_master_confirmation_errors


class LandingBlueprintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / 'run.json').write_text(json.dumps({'user_checkpoint':'complete-landing'}))
        self.p = root / 'project'
        self.p.mkdir()
        (self.p / 'content-architecture.md').write_text('## Sitemap / page or section outline\n\n| Scene ID | Section |\n|---|---|\n| SCN-001 | Hero |\n| SCN-002 | Close |\n')
        (self.p / 'creative-direction.md').write_text('internal master')
        (self.p / 'visual-system.md').write_text('## Complete landing blueprint\nPAGE_DESKTOP: desktop.png\nPAGE_MOBILE: mobile.png\n\n### Scene visual opportunities\n\n| Scene | Description |\n|---|---|\n| SCN-001 | hero |\n| SCN-002 | close |\n')
        for name in ('desktop.png','mobile.png'):
            (self.p / name).write_bytes(b'\x89PNG\r\n\x1a\nfixture')
        (self.p / '.reviews').mkdir()
        self.review = {'stage':'design-review','provider':'CODEX_SUBSCRIPTION','response_id':'test-review','images':['desktop.png','mobile.png'],'inputs':_snapshot(self.p,'design-review',['desktop.png','mobile.png']),'result':{'verdict':'PASS'}}
        (self.p / '.reviews/design-review.json').write_text(json.dumps(self.review))

    def test_only_checkpoint_moves_from_master_to_complete_proposal(self):
        self.assertEqual([], creative_master_confirmation_errors(self.p))
        self.assertTrue(design_approval_errors(self.p))
        self.assertEqual([], blueprint_errors(self.p))
        record_design_approval(self.p,'APPROVED','Apruebo esta propuesta completa')
        self.assertEqual([], design_approval_errors(self.p))

    def test_missing_scene_and_missing_page_block(self):
        path = self.p / 'visual-system.md'
        path.write_text(path.read_text().replace('| SCN-002 | close |',''))
        (self.p / 'mobile.png').rename(self.p / 'not-presented.png')
        self.assertEqual(2,len(blueprint_errors(self.p)))

    def test_changed_design_invalidates_approval(self):
        record_design_approval(self.p,'DELEGATED','Delegar la decisión')
        (self.p / 'desktop.png').write_bytes(b'changed')
        self.assertTrue(design_approval_errors(self.p))

    def test_adjust_does_not_authorize_build(self):
        record_design_approval(self.p,'ADJUST','Aumenta el contraste del cierre')
        self.assertTrue(design_approval_errors(self.p))

    def test_legacy_runs_are_not_silently_migrated(self):
        (self.p.parent / 'run.json').write_text('{}')
        self.assertEqual([], design_approval_errors(self.p))
        self.assertTrue(creative_master_confirmation_errors(self.p))
