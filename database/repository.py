from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
from typing import Any

from agent.models import Document


class WarehouseRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def connection(self):
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY,
                    warehouse TEXT NOT NULL,
                    sku TEXT NOT NULL,
                    description TEXT NOT NULL,
                    on_hand TEXT NOT NULL,
                    reserved TEXT NOT NULL DEFAULT '0',
                    unit TEXT NOT NULL,
                    UNIQUE(warehouse, sku)
                );
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    document_no TEXT NOT NULL UNIQUE,
                    document_date TEXT NOT NULL,
                    warehouse TEXT NOT NULL,
                    pallet_type TEXT,
                    movement TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    source_hash TEXT NOT NULL,
                    confirmed_by TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def seed_synthetic_inventory(self) -> None:
        rows = [
            ("WH-A", "SKU-001", "匿名測試零件 A", "100", "10", "PCS"),
            ("WH-A", "SKU-002", "匿名測試零件 B", "24", "0", "BOX"),
            ("WH-B", "SKU-003", "匿名測試零件 C", "50", "5", "PCS"),
        ]
        with self.connection() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO inventory(warehouse,sku,description,on_hand,reserved,unit) VALUES(?,?,?,?,?,?)",
                rows,
            )

    def get_inventory(self, warehouse: str | None) -> list[dict[str, Any]]:
        if not warehouse:
            return []
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT id, warehouse, sku, description, on_hand, reserved, unit FROM inventory WHERE warehouse = ?",
                (warehouse,),
            ).fetchall()
        result = []
        for row in rows:
            value = dict(row)
            value["on_hand"] = Decimal(value["on_hand"])
            value["reserved"] = Decimal(value["reserved"])
            result.append(value)
        return result

    def find_document(self, document_no: str | None) -> list[dict[str, Any]]:
        if not document_no:
            return []
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM documents WHERE document_no = ?", (document_no,)).fetchall()
        return [dict(row) for row in rows]

    def insert_document(self, document: Document, source_hash: str, actor: str) -> int:
        if not document.document_no or not document.document_date or not document.warehouse:
            raise ValueError("Critical fields are required before writing")
        payload = asdict(document)
        for item in payload["items"]:
            item["quantity"] = str(item["quantity"])
        try:
            with self.connection() as conn:
                cursor = conn.execute(
                    """INSERT INTO documents(document_no,document_date,warehouse,pallet_type,movement,payload_json,source_hash,confirmed_by)
                       VALUES(?,?,?,?,?,?,?,?)""",
                    (
                        document.document_no,
                        document.document_date,
                        document.warehouse,
                        document.pallet_type,
                        document.movement,
                        json.dumps(payload, ensure_ascii=False),
                        source_hash,
                        actor,
                    ),
                )
                return int(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            raise ValueError("DUPLICATE_DOCUMENT_WRITE_BLOCKED") from exc

    def append_audit(self, trace_id: str, action: str, payload: dict[str, Any]) -> None:
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO audit_log(trace_id,action,payload_json) VALUES(?,?,?)",
                (trace_id, action, json.dumps(payload, ensure_ascii=False, default=str)),
            )

    def audit_events(self, trace_id: str) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM audit_log WHERE trace_id = ? ORDER BY id", (trace_id,)).fetchall()
        return [dict(row) for row in rows]
