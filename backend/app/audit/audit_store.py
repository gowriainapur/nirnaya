"""
Procurement Compass - Append-Only Audit Trail Store
Uses SQLite for persistent, reproducible, and verifiable assessment records (§38, §56).
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "procurement_compass.db"

class AuditStore:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(str(self.db_path))

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_records (
                assessment_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                procurement_date TEXT,
                input_hash TEXT NOT NULL,
                user_input_json TEXT NOT NULL,
                ruleset_version TEXT NOT NULL,
                classification TEXT NOT NULL,
                route TEXT NOT NULL,
                status TEXT NOT NULL,
                decision_object_json TEXT NOT NULL,
                retrieval_mode TEXT NOT NULL,
                retrieved_chunk_ids TEXT NOT NULL,
                verification_result_json TEXT NOT NULL,
                generation_backend TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def compute_input_hash(self, inp_dict: Dict[str, Any]) -> str:
        s = json.dumps(inp_dict, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def save_record(
        self,
        assessment_id: str,
        procurement_date: Optional[str],
        user_input: Dict[str, Any],
        ruleset_version: str,
        classification: str,
        route: str,
        status: str,
        decision_object: Dict[str, Any],
        retrieval_mode: str,
        retrieved_chunk_ids: List[str],
        verification_result: Dict[str, Any],
        generation_backend: str = "deterministic_verified"
    ):
        conn = self.get_connection()
        cursor = conn.cursor()
        now_ts = datetime.utcnow().isoformat() + "Z"
        inp_hash = self.compute_input_hash(user_input)

        cursor.execute("""
            INSERT OR REPLACE INTO audit_records (
                assessment_id, timestamp, procurement_date, input_hash,
                user_input_json, ruleset_version, classification, route,
                status, decision_object_json, retrieval_mode, retrieved_chunk_ids,
                verification_result_json, generation_backend
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            assessment_id,
            now_ts,
            procurement_date or "",
            inp_hash,
            json.dumps(user_input),
            ruleset_version,
            classification,
            route,
            status,
            json.dumps(decision_object),
            retrieval_mode,
            json.dumps(retrieved_chunk_ids),
            json.dumps(verification_result),
            generation_backend
        ))
        conn.commit()
        conn.close()

    def get_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT assessment_id, timestamp, procurement_date, input_hash,
                   classification, route, status, ruleset_version,
                   retrieval_mode, retrieved_chunk_ids, decision_object_json,
                   verification_result_json, generation_backend
            FROM audit_records
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        records = []
        for r in rows:
            records.append({
                "assessment_id": r[0],
                "timestamp": r[1],
                "procurement_date": r[2],
                "input_hash": r[3],
                "classification": r[4],
                "route": r[5],
                "status": r[6],
                "ruleset_version": r[7],
                "retrieval_mode": r[8],
                "retrieved_chunk_ids": json.loads(r[9]),
                "decision_object": json.loads(r[10]),
                "verification_result": json.loads(r[11]),
                "generation_backend": r[12]
            })
        return records

    def get_by_id(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_records WHERE assessment_id = ?", (assessment_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "assessment_id": row[0],
            "timestamp": row[1],
            "procurement_date": row[2],
            "input_hash": row[3],
            "user_input": json.loads(row[4]),
            "ruleset_version": row[5],
            "classification": row[6],
            "route": row[7],
            "status": row[8],
            "decision_object": json.loads(row[9]),
            "retrieval_mode": row[10],
            "retrieved_chunk_ids": json.loads(row[11]),
            "verification_result": json.loads(row[12]),
            "generation_backend": row[13]
        }
