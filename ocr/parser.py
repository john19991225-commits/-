from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from agent.models import Document, Evidence, LineItem


FIELD_PATTERNS = {
    "document_no": r"(?:DOCUMENT[_ ]?NO|DOC[_ ]?NO|單據編號)\s*[:：]\s*(.+)",
    "document_date": r"(?:DATE|日期)\s*[:：]\s*(\d{4}[-/]\d{2}[-/]\d{2})",
    "warehouse": r"(?:WAREHOUSE|倉別)\s*[:：]\s*(.+)",
    "pallet_type": r"(?:PALLET[_ ]?TYPE|棧板型式)\s*[:：]\s*(.+)",
}
ITEM_PATTERN = re.compile(
    r"(?:ITEM|品項)\s*[:：]\s*([^|,]+)\s*[|,]\s*([^|,]+)\s*[|,]\s*([-+]?\d+(?:\.\d+)?)\s*[|,]\s*([^|,]+)",
    re.IGNORECASE,
)


def parse_document(text: str, evidence: list[Evidence], movement: str) -> Document:
    fields: dict[str, str | None] = {}
    field_evidence: dict[str, list[str]] = {}
    for name, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        fields[name] = match.group(1).strip() if match else None
        if match:
            ids = [e.evidence_id for e in evidence if match.group(0) in e.text]
            field_evidence[name] = ids
    if fields["document_date"]:
        fields["document_date"] = fields["document_date"].replace("/", "-")

    items: list[LineItem] = []
    for match in ITEM_PATTERN.finditer(text):
        try:
            quantity = Decimal(match.group(3))
        except InvalidOperation:
            continue
        ids = [e.evidence_id for e in evidence if match.group(0) in e.text]
        items.append(
            LineItem(
                sku=match.group(1).strip().upper(),
                description=match.group(2).strip(),
                quantity=quantity,
                unit=match.group(4).strip().upper(),
                evidence_ids=ids,
            )
        )
    return Document(
        document_no=fields["document_no"],
        document_date=fields["document_date"],
        warehouse=fields["warehouse"],
        pallet_type=fields["pallet_type"],
        movement=movement,
        items=items,
        field_evidence=field_evidence,
    )

