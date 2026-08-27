import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from reopen_project import reopen
from validation_release_integrity import (
    content_lock_build_errors,
    content_lock_definition_errors,
    implementation_digest,
    integrity_manifest_errors,
    runtime_traversal_errors,
    write_manifest,
)


class ReleaseIntegrityTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        project = Path(temporary.name) / "project"
        site = Path(temporary.name) / "site"
        evidence = project / "evidence"
        evidence.mkdir(parents=True)
        site.mkdir()
        (site / "index.html").write_text(
            "<h1>Invisible expertise, made concrete</h1><a>Request the diagnostic</a>",
            encoding="utf-8",
        )
        content = """# Content

## Sitemap / page or section outline
| Scene ID | Section | User question / job | Available content and assets | Importance (`PRIMARY | UTILITY`) |
|---|---|---|---|---|
| SCN-001 | Hero | Understand the thesis | Copy | PRIMARY |

## Content lock
| Content ID | Role (`HERO_THESIS | PRIMARY_CTA | NAVIGATION | CLAIM | PROOF | BODY | LEGAL`) | Exact approved text | Build requirement (`REQUIRED | OPTIONAL | OMIT`) | Intended scene / use |
|---|---|---|---|---|
| CNT-001 | HERO_THESIS | Invisible expertise, made concrete | REQUIRED | SCN-001 hero |
| CNT-002 | PRIMARY_CTA | Request the diagnostic | REQUIRED | SCN-001 action |
"""
        (project / "content-architecture.md").write_text(content, encoding="utf-8")
        for name in ("creative-direction.md", "visual-system.md", "production-plan.md", "technology-decision.md"):
            (project / name).write_text(f"# {name}\nverified fixture\n", encoding="utf-8")
        for viewport in ("desktop", "mobile"):
            (evidence / f"hero-{viewport}.png").write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        digest = implementation_digest(site)
        qa = f"""# QA

### Runtime traversal
| Scene ID | Viewport (`DESKTOP | MOBILE`) | Trigger / input | Expected state or transition | Observed result | Physical evidence relative to project | Verdict (`PASS | REVISE`) | Source digest |
|---|---|---|---|---|---|---|---|
| SCN-001 | DESKTOP | Load first viewport | Thesis and CTA are visible | Thesis and CTA remain visible | evidence/hero-desktop.png | PASS | sha256:{digest} |
| SCN-001 | MOBILE | Load narrow viewport | Thesis and CTA are visible | Thesis and CTA remain visible | evidence/hero-mobile.png | PASS | sha256:{digest} |

RELEASE_INTEGRITY_MANIFEST: evidence/release-integrity.json
"""
        (project / "qa-release.md").write_text(qa, encoding="utf-8")
        return temporary, project, site

    def test_content_lock_reaches_build(self):
        temporary, project, site = self.fixture()
        try:
            self.assertEqual(content_lock_definition_errors(project), [])
            self.assertEqual(content_lock_build_errors(project, site), [])
            (site / "index.html").write_text("<h1>Changed thesis</h1>", encoding="utf-8")
            errors = content_lock_build_errors(project, site)
            self.assertTrue(any("CNT-001 is absent" in error for error in errors))
        finally:
            temporary.cleanup()

    def test_runtime_traversal_rejects_reused_or_stale_evidence(self):
        temporary, project, site = self.fixture()
        try:
            self.assertEqual(runtime_traversal_errors(project, site), [])
            qa = (project / "qa-release.md").read_text(encoding="utf-8")
            qa = qa.replace("evidence/hero-mobile.png", "evidence/hero-desktop.png")
            (project / "qa-release.md").write_text(qa, encoding="utf-8")
            self.assertTrue(any("reuses evidence" in error for error in runtime_traversal_errors(project, site)))
        finally:
            temporary.cleanup()

    def test_manifest_invalidates_changed_code_and_upstream_artifact(self):
        temporary, project, site = self.fixture()
        try:
            write_manifest(project, site)
            self.assertEqual(integrity_manifest_errors(project, site), [])
            (site / "index.html").write_text("<h1>Changed</h1>", encoding="utf-8")
            self.assertTrue(any("implementation changed" in error for error in integrity_manifest_errors(project, site)))
            write_manifest(project, site)
            path = project / "visual-system.md"
            path.write_text(path.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
            self.assertTrue(any("visual-system.md changed" in error for error in integrity_manifest_errors(project, site)))
        finally:
            temporary.cleanup()

    def test_only_00_can_reopen_and_downstream_is_invalidated(self):
        temporary, project, _site = self.fixture()
        try:
            status = json.loads((ROOT / "templates/project/status.json").read_text(encoding="utf-8"))
            for item in status["gates"].values():
                item.update(status="APPROVED", evidence=["fixture"], blockers=[], last_decision="approved")
            for item in status["checkpoints"].values():
                item.update(status="APPROVED", evidence=["fixture"], blockers=[], last_decision="approved")
            (project / "status.json").write_text(json.dumps(status), encoding="utf-8")
            with self.assertRaises(ValueError):
                reopen(project, "G2", "master drift detected", "07")
            reopen(project, "G2", "master drift detected", "00")
            changed = json.loads((project / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(changed["gates"]["G2"]["status"], "PENDING")
            self.assertEqual(changed["checkpoints"]["direction-divergence"]["status"], "ACTIVE")
            self.assertEqual(changed["gates"]["G4"]["status"], "PENDING")
            self.assertFalse(changed["release"]["eligible"])
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
