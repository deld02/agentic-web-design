"""Benchmark attachment checks, not an empirical evaluation of artistic taste."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from harness_review import benchmark_images, review_axes, REVIEW_INSTRUCTIONS, correction_contract_errors, revision_stage, _schema
import json


class ArtisticBenchmarkTests(unittest.TestCase):
    def test_missing_research_blocks_review(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'ARTISTIC_BENCHMARK_REQUIRED'):
                benchmark_images(Path(directory))

    def test_existing_references_are_attached_once(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            from PIL import Image
            for name in ('excellent.png', 'generic.png'):
                Image.new('RGB', (32, 32)).save(project / name)
            rows = '\n'.join('| Name | '+role+' | search | observation | fit | adapt | https://example.com | 2026-09-29 | '+name+' |'
                             for role, name in [('FRONTIER','excellent.png'), ('SIMPLE','excellent.png'), ('SATURATED','generic.png')])
            (project / 'research-strategy.md').write_text('### Live website benchmark\n| Website | Role | Source | Observation | Fit | Use | URL | Date | Capture |\n|---|---|---|---|---|---|---|---|---|\n'+rows, encoding='utf-8')
            with patch('harness_review.inspect_raster', return_value={}):
                self.assertEqual(benchmark_images(project), ['excellent.png', 'generic.png'])
            (project / 'generic.png').unlink()
            with self.assertRaisesRegex(ValueError, 'invalid reference'):
                benchmark_images(project)

    def test_review_axes_and_instructions_allow_no_winner(self):
        axes = review_axes(Path('.'), Path('.'), 'direction-review')
        self.assertIn('reference_calibration', axes)
        self.assertIn('artistic_authority', axes)
        self.assertIn('reject every direction', REVIEW_INSTRUCTIONS)

    def test_root_diagnosis_is_required_and_consistent(self):
        self.assertIn('correction_kind', _schema(['composition'])['required'])
        self.assertTrue(correction_contract_errors({'verdict':'PASS'}))
        self.assertTrue(correction_contract_errors({'verdict':'PASS','correction_kind':'CONCEPT'}))
        self.assertTrue(correction_contract_errors({'verdict':'REVISE','correction_kind':'NONE','findings':['gap']}))
        self.assertTrue(correction_contract_errors({'verdict':'REVISE','correction_kind':'CONCEPT','findings':[]}))
        self.assertEqual([], correction_contract_errors({'verdict':'PASS','correction_kind':'NONE','findings':[]}))
        for kind in ('CRAFT','CONCEPT','REFERENCE'):
            self.assertEqual([], correction_contract_errors({'verdict':'REVISE','correction_kind':kind,'findings':['visible gap']}))

    def test_reference_failure_cannot_open_downstream_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / '.reviews').mkdir()
            record = project / '.reviews/direction-review.json'
            for kind, expected in [('REFERENCE',None),('CONCEPT','direction-divergence'),('CRAFT','direction-divergence')]:
                record.write_text(json.dumps({'result':{'verdict':'REVISE','correction_kind':kind}}))
                self.assertEqual(expected, revision_stage(project,'direction-review'))
            (project / '.reviews/direction-review-attempts.json').write_text('{"count":2}')
            self.assertIsNone(revision_stage(project,'direction-review'))

    def test_reviewer_does_not_require_literal_category_symbols(self):
        self.assertIn('Nonliteral imagery is valid', REVIEW_INSTRUCTIONS)
        self.assertIn('audience, action, trust', REVIEW_INSTRUCTIONS)

    def test_review_checks_anchor_choice_without_a_default_aesthetic(self):
        # Wiring regression only: this does not prove a model's artistic judgment.
        self.assertIn('communication-anchor selection from execution', REVIEW_INSTRUCTIONS)
        self.assertIn('strongest credible direct/evidence-led alternative', REVIEW_INSTRUCTIONS)
        self.assertIn('CONCEPT', REVIEW_INSTRUCTIONS)
        self.assertIn('Do not prefer portraits, abstraction or any aesthetic universally', REVIEW_INSTRUCTIONS)

    def test_context_reference_is_attached_without_duplicate_images(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            from PIL import Image
            for name in ('craft.png','risk.png','context.png'):
                Image.new('RGB',(32,32)).save(project/name)
            entries = [('FRONTIER','craft.png'),('SIMPLE','craft.png'),('SATURATED','risk.png'),('ADJACENT','context.png'),('DIRECT','context.png')]
            rows = '\n'.join('| Site | '+role+' | search | observation | fit | adapt | https://example.com | 2026-09-30 | '+name+' |' for role,name in entries)
            (project/'research-strategy.md').write_text('### Live website benchmark\n| Website | Role | Source | Observation | Fit | Use | URL | Date | Capture |\n|---|---|---|---|---|---|---|---|---|\n'+rows)
            self.assertEqual(['craft.png','risk.png','context.png'], benchmark_images(project))


if __name__ == '__main__':
    unittest.main()
