from fastapi.testclient import TestClient

from aims_logger import AIMSLogger
from main import app


client = TestClient(app)


def payload(client_id: str = "C-200") -> dict:
    return {
        "ips": {
            "client_id": client_id,
            "risk_score": 5,
            "time_horizon_years": 10,
            "liquidity_needs_usd": 10000,
            "tax_bracket_pct": 24,
        },
        "portfolio": {
            "client_id": client_id,
            "holdings": [
                {"symbol": "EQUITY", "asset_class": "Equity", "shares": 70, "current_price": 100, "cost_basis": 80},
                {"symbol": "BOND", "asset_class": "Fixed Income", "shares": 25, "current_price": 100, "cost_basis": 100},
                {"symbol": "CASH", "asset_class": "Cash", "shares": 5, "current_price": 100, "cost_basis": 100},
            ],
        },
    }


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rebalance_returns_audited_proposal(monkeypatch):
    monkeypatch.setattr(AIMSLogger, "log_rebalance_event", lambda **kwargs: "SEC-AUDIT-TEST")
    response = client.post("/api/v1/rebalance", json=payload())
    assert response.status_code == 200
    assert response.json()["compliance_approved"] is True
    assert response.json()["audit_id"] == "SEC-AUDIT-TEST"


def test_rebalance_rejects_mismatched_client_ids():
    request = payload()
    request["portfolio"]["client_id"] = "C-201"
    response = client.post("/api/v1/rebalance", json=request)
    assert response.status_code == 422
