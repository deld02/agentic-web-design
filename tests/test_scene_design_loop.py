"""Structural enforcement of the bounded section loop; no beauty scoring."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from validation_landing_blueprint import scene_design_loop_errors


class SceneDesignLoopTests(unittest.TestCase):
    def check(self, rows, missing=False):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            project = run / 'project'
            project.mkdir()
            (run / 'run.json').write_text(json.dumps({'user_checkpoint':'complete-landing'}), encoding='utf-8')
            (project / 'content-architecture.md').write_text('## Sitemap / page or section outline\n| Scene ID | Job |\n|---|---|\n| SCN-001 | Opening |\n| SCN-002 | Action |\n', encoding='utf-8')
            if not missing:
                (project / 'desktop.png').write_bytes(b'\x89PNG\r\n\x1a\n')
                (project / 'mobile.png').write_bytes(b'\x89PNG\r\n\x1a\n')
            (project / 'visual-system.md').write_text('### Section design loop\n| Scene | Attempt | Desktop | Mobile | Diagnosis | Result |\n|---|---|---|---|---|---|\n' + '\n'.join(f'| {scene} | {attempt} | desktop.png | mobile.png | Visible gain against reference | {result} |' for scene, attempt, result in rows), encoding='utf-8')
            return scene_design_loop_errors(project)

    def test_first_pass_and_directed_correction(self):
        self.assertEqual(self.check([('SCN-001',1,'PASS'), ('SCN-002',1,'REVISE'), ('SCN-002',2,'PASS')]), [])

    def test_skipping_unresolved_section_is_blocked(self):
        self.assertTrue(self.check([('SCN-001',1,'REVISE'), ('SCN-002',1,'PASS')]))

    def test_second_rejection_is_blocked(self):
        self.assertTrue(self.check([('SCN-001',1,'REVISE'), ('SCN-001',2,'REVISE')]))

    def test_missing_scene_or_physical_evidence_is_blocked(self):
        self.assertTrue(self.check([('SCN-001',1,'PASS')]))
        self.assertTrue(self.check([('SCN-001',1,'PASS'), ('SCN-002',1,'PASS')], missing=True))

    def test_legacy_run_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(scene_design_loop_errors(Path(temporary)), [])


if __name__ == '__main__':
    unittest.main()
