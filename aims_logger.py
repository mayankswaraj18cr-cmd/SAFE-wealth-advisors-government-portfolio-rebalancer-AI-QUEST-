import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

from config import settings


class AIMSLogger:
    @staticmethod
    def log_rebalance_event(client_id: str, orders: list[dict], suitability_passed: bool, notes: list[str]) -> str:
        audit_id = f"SEC-AUDIT-{uuid.uuid4().hex[:8].upper()}"
        payload = {
            "audit_id": audit_id,
            "client_id": client_id,
            "suitability_passed": suitability_passed,
            "orders_count": len(orders),
            "compliance_notes": notes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if settings.aims_endpoint:
            try:
                response = requests.post(settings.aims_endpoint, json=payload, timeout=3)
                response.raise_for_status()
                return audit_id
            except requests.RequestException:
                pass

        with Path("sec_compliance_audit.log").open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(payload) + "\n")
        return audit_id
