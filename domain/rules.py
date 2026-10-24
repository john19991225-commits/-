from __future__ import annotations

from agent.models import Document, Finding


ALLOWED_PALLETS = {"WOOD", "PLASTIC", "木棧板", "塑膠棧板"}


def evaluate_rules(document: Document, inventory: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    required = {
        "document_no": (document.document_no, "MISSING_DOCUMENT_NO", "缺少單據編號"),
        "document_date": (document.document_date, "MISSING_DATE", "缺少日期"),
        "warehouse": (document.warehouse, "MISSING_WAREHOUSE", "缺少倉別"),
        "pallet_type": (document.pallet_type, "MISSING_PALLET_TYPE", "缺少棧板型式"),
    }
    for field_name, (value, code, message) in required.items():
        if not value:
            severity = "HIGH" if field_name != "pallet_type" else "MEDIUM"
            findings.append(Finding(code, severity, message, document.field_evidence.get(field_name, [])))
    if not document.items:
        findings.append(Finding("NO_ITEMS", "HIGH", "單據沒有可解析品項。"))
    for item in document.items:
        if item.quantity <= 0:
            findings.append(Finding("INVALID_QUANTITY", "HIGH", f"{item.sku} 數量必須大於零。", item.evidence_ids))
        if item.unit not in {"PCS", "BOX", "EA", "件", "箱"}:
            findings.append(Finding("UNKNOWN_UNIT", "MEDIUM", f"未支援單位 {item.unit}。", item.evidence_ids))
    if document.pallet_type and document.pallet_type.upper() not in ALLOWED_PALLETS:
        findings.append(
            Finding(
                "UNKNOWN_PALLET_TYPE",
                "MEDIUM",
                f"未知棧板型式 {document.pallet_type}。",
                document.field_evidence.get("pallet_type", []),
            )
        )
    return findings

