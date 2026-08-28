import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(project, implementation):
    return subprocess.run(
        [sys.executable, str(ROOT/'tools/validate_delivery.py'), '--project-dir', str(project), '--implementation-root', str(implementation)],
        text=True, capture_output=True, encoding='cp1252', errors='replace'
    )


class DeliveryValidationTests(unittest.TestCase):
    def fixture(self, reference='assets/hero.png', payload=b'\x89PNG\r\n\x1a\nvalid-image-data', role_method='PRIMARY:EXTERNAL_IMAGE_LOOP'):
        td = tempfile.TemporaryDirectory(); base = Path(td.name)
        project = base/'project'; implementation = base/'site'; asset = implementation/reference
        project.mkdir(); asset.parent.mkdir(parents=True)
        (project/'production-plan.md').write_text(
            '# Production Plan\n\n## Asset inventory and readiness\n\n| ID | Scene / function | What it represents | Payload role / selected method | Status | Final file / fallback |\n|---|---|---|---|---|---|\n'
            f'| IMG-001 | Hero | Editorial subject | {role_method} | FINAL | {reference} |\n\n## Image decision sheets\n\n'
            '### Material effect decisions\n\n'
            '| Effect ID / scene | Opportunity level | Static candidate | Simple candidate | Expressive candidate | Source anchors / transfer | Evaluation / winner | Prototype evidence | Fallback / owner | Status (`FINAL | STATIC_WINNER_REVIEWED`) | Implementation proof |\n'
            '|---|---|---|---|---|---|---|---|---|---|---|\n'
            '| FX-001 / hero | defining | still | reveal | assembly | live + lab | reveal wins | prototype | static / 05 | FINAL | index.html#data-fx-hero | FLAT_2D |\n', encoding='utf-8')
        (project/'brief.md').write_text('# Brief\n', encoding='utf-8')
        asset.write_bytes(payload)
        (implementation/'index.html').write_text(
            f'<style>[data-fx-hero]{{transition:transform .3s ease}}</style><main data-fx-hero><img src="{reference}" alt="Editorial subject"></main>',
            encoding='utf-8')
        return td, project, implementation, asset

    def test_real_integrated_asset_passes(self):
        td, project, implementation, _asset = self.fixture()
        try:
            result = run(project, implementation)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        finally: td.cleanup()

    def test_pipeline_cannot_claim_direct_final_generation(self):
        td, project, implementation, _asset = self.fixture(role_method='PRIMARY:CHATGPT_GENERATE')
        try:
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('invalid payload role/method', result.stdout)
        finally: td.cleanup()

    def test_declared_but_missing_asset_fails(self):
        td, project, implementation, asset = self.fixture()
        try:
            asset.unlink()
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0); self.assertIn('does not exist', result.stdout)
        finally: td.cleanup()

    def test_unintegrated_asset_fails(self):
        td, project, implementation, _asset = self.fixture()
        try:
            (implementation/'index.html').write_text('<main>No visual reference</main>', encoding='utf-8')
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0); self.assertIn('not referenced', result.stdout)
        finally: td.cleanup()

    def test_full_page_capture_cannot_be_asset(self):
        td, project, implementation, _asset = self.fixture('assets/mobile-full.png')
        try:
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0); self.assertIn('capture cannot be a landing asset', result.stdout)
        finally: td.cleanup()

    def test_fake_image_extension_fails(self):
        td, project, implementation, _asset = self.fixture(payload=b'not a real png')
        try:
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0); self.assertIn('does not match a valid visual format', result.stdout)
        finally: td.cleanup()

    def test_final_effect_without_implementation_proof_fails(self):
        td, project, implementation, _asset = self.fixture()
        try:
            plan=project/'production-plan.md'
            plan.write_text(plan.read_text(encoding='utf-8').replace('index.html#data-fx-hero',''),encoding='utf-8')
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0); self.assertIn('needs source/file#marker', result.stdout)
        finally: td.cleanup()

    def test_final_effect_must_name_its_real_medium(self):
        td, project, implementation, _asset = self.fixture()
        try:
            plan=project/'production-plan.md'
            plan.write_text(plan.read_text(encoding='utf-8').replace(' | FLAT_2D |',' | |'),encoding='utf-8')
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('delivered medium must be one of', result.stdout)
        finally: td.cleanup()

    def test_claimed_3d_requires_external_provenance(self):
        td, project, implementation, _asset = self.fixture()
        try:
            plan=project/'production-plan.md'
            plan.write_text(plan.read_text(encoding='utf-8').replace('FLAT_2D','INTERACTIVE_3D'),encoding='utf-8')
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('requires 3D production provenance', result.stdout)
        finally: td.cleanup()

    def test_css_perspective_cannot_prove_3d(self):
        td, project, implementation, _asset = self.fixture()
        try:
            plan=project/'production-plan.md'
            plan.write_text(
                plan.read_text(encoding='utf-8').replace('FLAT_2D','INTERACTIVE_3D')
                + '\n### 3D production provenance\n\n'
                + '| FX ID | Medium | External source / authoring tool | Asset / runtime | License or rights | Integration proof (`source/file#marker`) | Static / reduced-motion fallback |\n'
                + '|---|---|---|---|---|---|---|\n'
                + '| FX-001 | INTERACTIVE_3D | CSS | CSS perspective | owned | index.html#data-fx-hero | hero.png |\n',
                encoding='utf-8')
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('CSS/SVG is not 3D', result.stdout)
            self.assertIn('real model, scene, render tool or web runtime', result.stdout)
        finally: td.cleanup()

    def test_real_external_3d_provenance_passes(self):
        td, project, implementation, _asset = self.fixture()
        try:
            plan=project/'production-plan.md'
            plan.write_text(
                plan.read_text(encoding='utf-8').replace('FLAT_2D','INTERACTIVE_3D')
                + '\n### 3D production provenance\n\n'
                + '| FX ID | Medium | External source / authoring tool | Asset / runtime | License or rights | Integration proof (`source/file#marker`) | Static / reduced-motion fallback |\n'
                + '|---|---|---|---|---|---|---|\n'
                + '| FX-001 | INTERACTIVE_3D | Spline authored scene | Three.js + assets/scene.glb | original production rights | index.html#data-fx-hero | assets/hero.png |\n',
                encoding='utf-8')
            result = run(project, implementation)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        finally: td.cleanup()

    def test_cmp_design_evidence_cannot_ship_as_final_asset(self):
        td, project, implementation, _asset = self.fixture('assets/cmp-101.png')
        try:
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('CMP design evidence cannot be shipped', result.stdout)
        finally: td.cleanup()

    def test_supporting_svg_cannot_satisfy_visual_payload(self):
        td, project, implementation, _asset = self.fixture(role_method='SUPPORTING:SVG_OR_CSS')
        try:
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('no FINAL PRIMARY scene-bearing visual', result.stdout)
        finally: td.cleanup()

    def test_svg_cannot_be_the_only_primary_visual(self):
        td, project, implementation, _asset = self.fixture('assets/hero.svg', b'<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>', 'PRIMARY:SVG_OR_CSS')
        try:
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('SVG/vector cannot be the only PRIMARY', result.stdout)
        finally: td.cleanup()

    def test_review_marker_cannot_bypass_primary_media_requirement(self):
        td, project, implementation, _asset = self.fixture('assets/hero.svg', b'<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>', 'PRIMARY:CUSTOM_ILLUSTRATION')
        try:
            (project/'visual-system.md').write_text(
                '# Visual\n\n## Independent design review and findings\n\nVECTOR_PRIMARY_REVIEWED: rendered custom illustration carries the material transformation; raster and 3D comparisons reduced clarity.\n',
                encoding='utf-8')
            (project/'status.json').write_text(json.dumps({'checkpoints': {'design-review': {'status': 'APPROVED', 'review_context': 'ISOLATED'}}}), encoding='utf-8')
            result = run(project, implementation)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('SVG/vector cannot be the only PRIMARY', result.stdout)
        finally: td.cleanup()
