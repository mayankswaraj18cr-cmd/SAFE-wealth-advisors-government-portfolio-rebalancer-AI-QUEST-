from fastapi import FastAPI, HTTPException

from aims_logger import AIMSLogger
from config import settings
from models import RebalanceProposal, RebalanceRequest
from rebalancer import DeterministicRebalancer
from safe_guard import LyzrSafeAIGuard

app = FastAPI(title=settings.app_name, version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.post("/api/v1/rebalance", response_model=RebalanceProposal)
def execute_rebalance(request: RebalanceRequest) -> RebalanceProposal:
    try:
        orders = DeterministicRebalancer.generate_orders(request.portfolio, request.ips)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    passed, violations = LyzrSafeAIGuard.validate_suitability(request.ips, orders)
    violations.extend(LyzrSafeAIGuard.validate_cash_buffer(request.portfolio))
    passed = not violations
    audit_id = AIMSLogger.log_rebalance_event(
        client_id=request.ips.client_id,
        orders=[order.model_dump() for order in orders],
        suitability_passed=passed,
        notes=violations,
    )
    if not passed:
        raise HTTPException(status_code=422, detail={"suitability_violations": violations, "audit_id": audit_id})

    return RebalanceProposal(
        client_id=request.ips.client_id,
        target_allocations=DeterministicRebalancer.compute_target_allocation(request.ips),
        orders=orders,
        compliance_approved=True,
        violations=[],
        audit_id=audit_id,
    )
