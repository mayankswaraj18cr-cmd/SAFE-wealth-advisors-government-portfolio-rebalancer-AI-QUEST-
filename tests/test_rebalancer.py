from models import Holding, IPSProfile, Portfolio, TradeOrder
from rebalancer import DeterministicRebalancer
from safe_guard import LyzrSafeAIGuard


def test_conservative_allocation_generates_sell_order():
    ips = IPSProfile(client_id="C-101", risk_score=2, time_horizon_years=10, liquidity_needs_usd=10000, tax_bracket_pct=24)
    portfolio = Portfolio(client_id="C-101", holdings=[
        Holding(symbol="VTI", asset_class="Equity", shares=100, current_price=200, cost_basis=150),
        Holding(symbol="BND", asset_class="Fixed Income", shares=50, current_price=80, cost_basis=80),
    ])
    orders = DeterministicRebalancer.generate_orders(portfolio, ips)
    assert orders
    assert orders[0].action == "SELL"


def test_prohibited_asset_is_rejected():
    ips = IPSProfile(client_id="C-102", risk_score=5, time_horizon_years=5, liquidity_needs_usd=5000, tax_bracket_pct=15)
    order = TradeOrder(symbol="MEME_COIN", action="BUY", shares=100, estimated_price=10, tax_impact_usd=0, reasoning="Speculative")
    passed, violations = LyzrSafeAIGuard.validate_suitability(ips, [order])
    assert not passed
    assert "CRITICAL" in violations[0]


def test_target_allocation_sums_to_one():
    ips = IPSProfile(client_id="C-103", risk_score=8, time_horizon_years=20, liquidity_needs_usd=0, tax_bracket_pct=0)
    assert sum(DeterministicRebalancer.compute_target_allocation(ips).values()) == 1
