from __future__ import annotations

import hashlib
import uuid

from agent.models import AnalysisResult, Finding
from agent.planner import RuleBasedPlanner
from analytics.checks import analyze_document
from database.repository import WarehouseRepository
from domain.rules import evaluate_rules
from ocr.base import OCRProvider
from ocr.parser import parse_document


class SmartWarehouseAgent:
    def __init__(self, repository: WarehouseRepository, ocr: OCRProvider) -> None:
        self.repository = repository
        self.ocr = ocr
        self.planner = RuleBasedPlanner()

    def analyze(self, query: str, content: bytes, filename: str) -> AnalysisResult:
        trace_id = str(uuid.uuid4())
        source_hash = hashlib.sha256(content).hexdigest()
        findings: list[Finding] = []
        evidence = []
        try:
            if not content:
                raise ValueError("EMPTY_FILE")
            intent, plan = self.planner.build_plan(query)
            ocr_output = self.ocr.extract(content, filename)
            evidence = ocr_output.evidence
            if not ocr_output.text.strip():
                raise ValueError("OCR_EMPTY_RESULT")
            document = parse_document(ocr_output.text, evidence, intent)
            history = self.repository.find_document(document.document_no)
            inventory = self.repository.get_inventory(document.warehouse)
            findings.extend(analyze_document(document, history, inventory))
            findings.extend(evaluate_rules(document, inventory))
            critical = {"MISSING_DOCUMENT_NO", "MISSING_DATE", "MISSING_WAREHOUSE", "NO_ITEMS"}
            confidence = min((e.confidence for e in evidence), default=0.0)
            human_required = bool(findings) or confidence < 0.75
            status = "HUMAN_REVIEW_REQUIRED" if human_required else "PASS_RECOMMENDED"
            if any(f.code in critical for f in findings):
                status = "REQUEST_CORRECTION"
            result = AnalysisResult(
                trace_id=trace_id,
                status=status,
                document=document,
                findings=findings,
                evidence=evidence,
                plan=plan,
                confidence=confidence,
                human_required=human_required,
                source_hash=source_hash,
            )
        except Exception as exc:
            result = AnalysisResult(
                trace_id=trace_id,
                status="FAILED",
                document=None,
                findings=findings,
                evidence=evidence,
                plan=[],
                confidence=0.0,
                human_required=True,
                source_hash=source_hash,
                error=str(exc),
            )
        self.repository.append_audit(trace_id, "ANALYZE", result.to_dict())
        return result

    def confirm_and_write(self, result: AnalysisResult, actor: str) -> int:
        if result.document is None or result.status == "FAILED":
            raise ValueError("No valid document is available for confirmation")
        if not actor.strip():
            raise ValueError("A confirming actor is required")
        row_id = self.repository.insert_document(result.document, result.source_hash, actor)
        self.repository.append_audit(
            result.trace_id,
            "HUMAN_CONFIRMED_WRITE",
            {"document_row_id": row_id, "actor": actor},
        )
        return row_id

