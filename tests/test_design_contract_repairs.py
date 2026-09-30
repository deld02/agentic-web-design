import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from project_validation import scene_visual_errors
from harness_review import run_visual_review, review_axes
import test_spatial_experience as spatial_fixtures


class DesignContractRepairs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.write('content-architecture.md', '## Sitemap / page or section outline\n\n| Scene ID | Section |\n|---|---|\n| SCN-001 | Umbral / hero |\n')
        self.write('visual-system.md', '### Scene visual opportunities\n\n| Scene | Job | Baseline | Mode | Desktop | Mobile | Decomposition | Decision |\n|---|---|---|---|---|---|---|---|\n| SCN-001 | thesis | enough | CSS_NATIVE | CMP-001:desktop.png | CMP-002:mobile.png | HTML/CSS + NO_IMAGE + NO_EFFECT | deliberate typography |\n')

    def write(self, name, text):
        (self.project / name).write_text(text, encoding='utf-8')

    def errors(self):
        with patch('project_validation._physical_composition_error', return_value=None):
            return scene_visual_errors(self.project)

    def test_scene_id_resolves_hero_and_no_media_is_valid(self):
        self.assertEqual([], self.errors())

    def test_missing_media_decision_is_not_silently_accepted(self):
        path = self.project / 'visual-system.md'
        self.write(path.name, path.read_text().replace(' + NO_IMAGE', ''))
        self.assertTrue(self.errors())

    def test_external_image_loop_cannot_claim_no_image(self):
        path = self.project / 'visual-system.md'
        self.write(path.name, path.read_text().replace('CSS_NATIVE', 'EXTERNAL_IMAGE_LOOP'))
        self.assertTrue(self.errors())

    def test_unknown_scene_is_not_invented_as_hero(self):
        self.write('content-architecture.md', '')
        self.assertIn('G3 requires a composed hero scene', self.errors())

    def test_preflight_failure_does_not_spend_provider_attempt(self):
        with patch.dict(os.environ, {'AGENTIC_AI_BACKEND': 'session'}), \
             patch('harness_review.benchmark_images', return_value=[]), \
             patch('harness_review._snapshot', return_value={}), \
             patch('project_validation.scene_visual_errors', return_value=['missing composition']), \
             patch('validation_spatial_experience.spatial_selection_errors', return_value=[]), \
             patch('harness_review.subscription_review') as provider:
            with self.assertRaisesRegex(ValueError, 'DESIGN_PREFLIGHT'):
                run_visual_review(ROOT, self.project, {'id':'design-review'}, ['desktop.png','mobile.png'])
            provider.assert_not_called()
        self.assertFalse((self.project / '.reviews').exists())

    def test_flat_does_not_require_separate_spatial_pass(self):
        from validation_spatial_experience import spatial_selection_errors
        fixture = spatial_fixtures.SpatialExperienceTests()
        tmp, project, _ = fixture.fixture()
        with tmp:
            fixture.write_selection(project, mode='FLAT_2D', review='PENDING')
            self.assertEqual([], spatial_selection_errors(project))

    def test_managed_spatial_cannot_self_approve(self):
        from validation_spatial_experience import spatial_selection_errors
        fixture = spatial_fixtures.SpatialExperienceTests()
        tmp, project, _ = fixture.fixture()
        with tmp:
            fixture.write_selection(project)
            (project / '.reviews').mkdir()
            self.assertTrue(any('independent' in e for e in spatial_selection_errors(project)))

    def test_spatial_axis_is_requested_only_for_selected_spatial_medium(self):
        for mode in ('FLAT_2D', 'LAYERED_2D', 'RENDERED_3D', 'INTERACTIVE_3D'):
            with self.subTest(mode=mode), patch('validation_spatial_experience.selected_spatial_mode', return_value=mode):
                self.assertEqual(mode != 'FLAT_2D', 'spatial_modality' in review_axes(ROOT, self.project, 'design-review'))
