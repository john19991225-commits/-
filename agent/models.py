from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class Evidence:
    evidence_id: str
    source: str
    text: str
    page: int = 1
    bbox: tuple[int, int, int, int] | None = None
    confidence: float = 1.0


@dataclass
class LineItem:
    sku: str
    description: str
    quantity: Decimal
    unit: str
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class Document:
    document_no: str | None
    document_date: str | None
    warehouse: str | None
    pallet_type: str | None
    movement: str
    items: list[LineItem]
    field_evidence: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class PlanStep:
    name: str
    tool: str
    reason: str


@dataclass
class AnalysisResult:
    trace_id: str
    status: str
    document: Document | None
    findings: list[Finding]
    evidence: list[Evidence]
    plan: list[PlanStep]
    confidence: float
    human_required: bool
    source_hash: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        if self.document:
            for item in value["document"]["items"]:
                item["quantity"] = str(item["quantity"])
        return value

