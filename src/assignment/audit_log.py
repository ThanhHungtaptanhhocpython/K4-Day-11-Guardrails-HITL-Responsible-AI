"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into ADK callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, float] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        key = request_id or user_id
        self._open[key] = datetime.now(timezone.utc).timestamp()
        self.logs.append({
            "event_type": "input",
            "user_id": user_id,
            "text": text,
            "request_id": request_id,
            "timestamp": utc_now_iso()
        })

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
        reviewer_decision: str | None = None,
    ):
        key = request_id or user_id
        start_time = self._open.pop(key, None)
        latency = None
        if start_time is not None:
            latency = datetime.now(timezone.utc).timestamp() - start_time
            
        self.logs.append({
            "event_type": "output",
            "user_id": user_id,
            "text": text,
            "blocked": blocked,
            "layer": layer,
            "request_id": request_id,
            "reviewer_decision": reviewer_decision,
            "timestamp": utc_now_iso(),
            "latency_seconds": latency
        })

    def export_json(self, filepath: str = "outputs/audit_log.json"):
        """Write logs to disk (JSON array)."""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
