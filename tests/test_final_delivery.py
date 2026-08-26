import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validation_final_delivery import final_delivery_contract_errors


def contract(**changes):
    values = {
        "DELIVERY_STATUS": "READY",
        "LANDING_ENTRY": "index.html",
        "RUN_COMMAND": "python -m http.server 8000",
        "BUILD_COMMAND": "NOT_REQUIRED",
        "PREVIEW_TARGET": "site/index.html",
        "DELIVERY_PACKAGE": "site",
        "ASSET_COMPLETENESS": "COMPLETE",
        "LIMITATIONS": "NONE",
        "HANDOFF_SUMMARY": "Distinctive responsive landing with integrated final media and verified interaction behavior.",
    }
    values.update(changes)
    return "\n".join(f"{key}: {value}" for key, value in values.items())


class FinalDeliveryContractTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        site = root / "site"
        site.mkdir()
        (site / "index.html").write_text("<main>Landing</main>", encoding="utf-8")
        return temporary, root, site

    def test_complete_clean_delivery_passes(self):
        temporary, root, site = self.fixture()
        try:
            self.assertEqual(final_delivery_contract_errors(contract(), root, site), [])
        finally:
            temporary.cleanup()

    def test_not_ready_delivery_is_blocked(self):
        temporary, root, site = self.fixture()
        try:
            errors = final_delivery_contract_errors(contract(DELIVERY_STATUS="NOT_READY"), root, site)
            self.assertIn("final delivery is NOT_READY", errors)
        finally:
            temporary.cleanup()

    def test_limited_status_requires_explicit_limitation(self):
        temporary, root, site = self.fixture()
        try:
            errors = final_delivery_contract_errors(
                contract(DELIVERY_STATUS="READY_WITH_LIMITATIONS"), root, site
            )
            self.assertIn("READY_WITH_LIMITATIONS requires an explicit limitation", errors)
        finally:
            temporary.cleanup()

    def test_internal_material_in_package_is_blocked(self):
        temporary, root, site = self.fixture()
        try:
            cache = site / "__pycache__"
            cache.mkdir()
            (cache / "build.pyc").write_bytes(b"cache")
            errors = final_delivery_contract_errors(contract(), root, site)
            self.assertTrue(any("internal/generated material" in error for error in errors))
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
