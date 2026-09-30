"""Causal design contracts; no automatic claim of aesthetic quality."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from validation_release_integrity import content_lock_definition_errors, semantic_resolution_errors, content_lock_build_errors
from harness_review import representative_images, review_axes
from validation_motion_payload import motion_payload_errors, reviewed_static_direction
from project_validation import direction_divergence_errors


class DesignDecisionArchitectureTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.p = Path(tmp.name) / 'project'
        self.p.mkdir()
        self.content = ('## Content lock\n| Content ID | Role | Meaning | Requirement | Scene | Lock |\n|---|---|---|---|---|---|\n'
                        '| CNT-001 | HERO_THESIS | Work becomes simpler | REQUIRED | SCN-001 | SEMANTIC |\n'
                        '| CNT-002 | PRIMARY_CTA | Contact our team | REQUIRED | SCN-003 | VERBATIM |\n')
        (self.p/'content-architecture.md').write_text(self.content)
        (self.p/'visual-system.md').write_text('### Editorial resolution\n| Content ID | Wording | Meaning | Scene |\n|---|---|---|---|\n| CNT-001 | Less friction. More focus. | Same promise, no performance claim | SCN-001 |\n')

    def test_semantic_wording_resolves_then_freezes_for_build(self):
        self.assertEqual([], content_lock_definition_errors(self.p))
        self.assertEqual([], semantic_resolution_errors(self.p))
        build = self.p/'implementation'
        build.mkdir()
        (build/'index.html').write_text('Less friction. More focus. Contact our team')
        self.assertEqual([], content_lock_build_errors(self.p, build))
        (build/'index.html').write_text('Work becomes simpler Contact our team')
        self.assertTrue(content_lock_build_errors(self.p, build))
        self.assertIn('content_semantics', review_axes(Path('.'), self.p, 'design-review'))

    def test_claims_cannot_be_reworded_as_semantic(self):
        (self.p/'content-architecture.md').write_text(self.content.replace('HERO_THESIS','CLAIM'))
        self.assertTrue(any('require VERBATIM' in e for e in content_lock_definition_errors(self.p)))

    def test_missing_semantic_resolution_blocks(self):
        (self.p/'visual-system.md').write_text('')
        self.assertTrue(semantic_resolution_errors(self.p))

    def test_legacy_content_lock_is_verbatim(self):
        text = self.content.replace(' | SEMANTIC |',' |').replace(' | VERBATIM |',' |')
        (self.p/'content-architecture.md').write_text(text)
        self.assertEqual([], semantic_resolution_errors(self.p))

    def test_representative_situations_reuse_scene_evidence(self):
        (self.p.parent/'run.json').write_text('{"user_checkpoint":"complete-landing"}')
        outline = '## Sitemap / page or section outline\n| Scene ID | Section |\n|---|---|\n'
        outline += '\n'.join(f'| SCN-00{i} | Section {i} |' for i in range(1,4))
        (self.p/'content-architecture.md').write_text(outline)
        visual = '### Scene visual opportunities\n| Scene | Job | Base | Mode | Desktop | Mobile | Decomposition | Reason |\n|---|---|---|---|---|---|---|---|\n'
        visual += '\n'.join(f'| SCN-00{i} | job | base | CSS_NATIVE | CMP-00{i}:d{i}.png | CMP-01{i}:m{i}.png | HTML/CSS | reason |' for i in range(1,4))
        (self.p/'visual-system.md').write_text(visual)
        self.assertEqual(['d1.png','m1.png','d2.png','m2.png','d3.png','m3.png'],representative_images(self.p))
        (self.p/'visual-system.md').write_text(visual.replace('| SCN-003 |','| SCN-009 |'))
        with self.assertRaisesRegex(ValueError,'SCN-003'):
            representative_images(self.p)

    def test_static_is_independently_reviewed_not_self_authorized(self):
        (self.p/'visual-system.md').write_text('MOTION_POLICY: STATIC\n')
        self.assertFalse(reviewed_static_direction(self.p))
        self.assertIn('motion_value',review_axes(Path('.'),self.p,'design-review'))
        (self.p/'.reviews').mkdir()
        record = {'result':{'axes':{'motion_value':{'status':'PASS'}}}}
        (self.p/'.reviews/design-review.json').write_text(json.dumps(record))
        with patch('harness_review.review_record_errors',return_value=[]):
            self.assertTrue(reviewed_static_direction(self.p))
            with patch('validation_motion_payload.explicit_static_only_authorized',return_value=False):
                (self.p/'production-plan.md').write_text('## Page visual narrative map\n| Scene ID | Beat | Job | Level | Format | Behavior |\n|---|---|---|---|---|---|\n| SCN-001 | ANCHOR | lead | high | BACKGROUND | STATIC |\n')
                self.assertEqual([],motion_payload_errors(self.p))
        with patch('harness_review.review_record_errors',return_value=['stale']):
            self.assertFalse(reviewed_static_direction(self.p))

    def test_direction_count_is_bounded_not_exactly_three(self):
        for count in (1,2,3,4,5):
            text = '## Direction divergence\n| Direction ID | Concept | Type | Composition | Media | Depth | Human | Board |\n|---|---|---|---|---|---|---|---|\n'
            text += '\n'.join(f'| DIR-00{i} | idea{i} | type{i} | comp{i} | media{i} | depth{i} | human{i} | d{i}.png |' for i in range(count))
            (self.p/'creative-direction.md').write_text(text)
            with patch('project_validation._physical_composition_error',return_value=None):
                errors = direction_divergence_errors(self.p,require_selection=False)
            self.assertEqual(count in (1,5), any('two to four' in e for e in errors))
