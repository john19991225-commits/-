from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent.service import SmartWarehouseAgent
from database.repository import WarehouseRepository
from ocr.providers import SyntheticOCRProvider
from ocr.providers import AutoOCRProvider


VALID = """DOCUMENT_NO: TEST-001
DATE: 2026-10-24
WAREHOUSE: WH-A
PALLET_TYPE: WOOD
ITEM: SKU-001 | Synthetic A | 5 | PCS
"""


class MVPIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.repo = WarehouseRepository(self.db_path)
        self.repo.initialize()
        self.repo.seed_synthetic_inventory()
        self.agent = SmartWarehouseAgent(self.repo, SyntheticOCRProvider())

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_end_to_end_requires_confirmation_then_writes(self) -> None:
        result = self.agent.analyze("check receipt", VALID.encode(), "fixture.png")
        self.assertEqual("PASS_RECOMMENDED", result.status)
        self.assertEqual("TEST-001", result.document.document_no)
        self.assertEqual(7, len(result.plan))
        self.assertEqual([], result.findings)
        self.assertEqual([], self.repo.find_document("TEST-001"))
        row_id = self.agent.confirm_and_write(result, "tester")
        self.assertGreater(row_id, 0)
        self.assertEqual(1, len(self.repo.find_document("TEST-001")))
        self.assertEqual(2, len(self.repo.audit_events(result.trace_id)))

    def test_duplicate_is_detected_and_second_write_blocked(self) -> None:
        first = self.agent.analyze("receipt", VALID.encode(), "a.png")
        self.agent.confirm_and_write(first, "tester")
        second = self.agent.analyze("receipt", VALID.encode(), "b.png")
        self.assertEqual("HUMAN_REVIEW_REQUIRED", second.status)
        self.assertIn("DUPLICATE_DOCUMENT", {f.code for f in second.findings})
        with self.assertRaisesRegex(ValueError, "DUPLICATE_DOCUMENT_WRITE_BLOCKED"):
            self.agent.confirm_and_write(second, "tester")

    def test_missing_fields_requests_correction(self) -> None:
        result = self.agent.analyze("receipt", b"PALLET_TYPE: WOOD", "missing.png")
        self.assertEqual("REQUEST_CORRECTION", result.status)
        codes = {f.code for f in result.findings}
        self.assertTrue({"MISSING_DOCUMENT_NO", "MISSING_DATE", "MISSING_WAREHOUSE", "NO_ITEMS"} <= codes)

    def test_empty_file_fails_safely(self) -> None:
        result = self.agent.analyze("receipt", b"", "empty.pdf")
        self.assertEqual("FAILED", result.status)
        self.assertEqual("EMPTY_FILE", result.error)
        self.assertTrue(result.human_required)

    def test_unavailable_image_ocr_fails_with_explicit_error(self) -> None:
        agent = SmartWarehouseAgent(self.repo, AutoOCRProvider())
        result = agent.analyze("receipt", b"not-a-real-image", "scan.png")
        self.assertEqual("FAILED", result.status)
        self.assertIn("TESSERACT", result.error)

    def test_issue_quantity_exceeding_available_is_flagged(self) -> None:
        content = VALID.replace("5 | PCS", "95 | PCS").replace("TEST-001", "TEST-002")
        result = self.agent.analyze("出庫檢查", content.encode(), "issue.png")
        self.assertEqual("HUMAN_REVIEW_REQUIRED", result.status)
        self.assertIn("INSUFFICIENT_STOCK", {f.code for f in result.findings})


if __name__ == "__main__":
    unittest.main()
