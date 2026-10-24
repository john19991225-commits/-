from __future__ import annotations

from agent.models import Document, Finding


def analyze_document(document: Document, history: list[dict], inventory: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    if history:
        findings.append(
            Finding(
                "DUPLICATE_DOCUMENT",
                "HIGH",
                f"單據編號 {document.document_no} 已存在 {len(history)} 筆紀錄。",
                document.field_evidence.get("document_no", []),
            )
        )
    inventory_by_sku = {row["sku"]: row for row in inventory}
    for item in document.items:
        row = inventory_by_sku.get(item.sku)
        if row is None:
            findings.append(Finding("UNKNOWN_SKU", "HIGH", f"品項 {item.sku} 不存在測試庫存。", item.evidence_ids))
            continue
        if document.movement == "ISSUE":
            available = row["on_hand"] - row["reserved"]
            if item.quantity > available:
                findings.append(
                    Finding(
                        "INSUFFICIENT_STOCK",
                        "HIGH",
                        f"{item.sku} 需求 {item.quantity}，可用量 {available}。",
                        item.evidence_ids + [f"db:inventory:{row['id']}"],
                    )
                )
    return findings

