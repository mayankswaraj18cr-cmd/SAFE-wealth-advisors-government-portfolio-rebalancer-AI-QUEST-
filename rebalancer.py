from typing import ClassVar

from config import settings
from models import IPSProfile, Portfolio, TradeOrder


class DeterministicRebalancer:
    ALLOCATION_BY_RISK: ClassVar[tuple[tuple[int, dict[str, float]], ...]] = (
        (3, {"Equity": 0.20, "Fixed Income": 0.65, "Commodity": 0.05, "Cash": 0.10}),
        (7, {"Equity": 0.60, "Fixed Income": 0.30, "Commodity": 0.05, "Cash": 0.05}),
    )
    AGGRESSIVE_ALLOCATION: ClassVar[dict[str, float]] = {
        "Equity": 0.80, "Fixed Income": 0.10, "Commodity": 0.05, "Cash": 0.05
    }

    @classmethod
    def compute_target_allocation(cls, ips: IPSProfile) -> dict[str, float]:
        for maximum_risk, allocation in cls.ALLOCATION_BY_RISK:
            if ips.risk_score <= maximum_risk:
                return allocation.copy()
        return cls.AGGRESSIVE_ALLOCATION.copy()

    @classmethod
    def generate_orders(cls, portfolio: Portfolio, ips: IPSProfile) -> list[TradeOrder]:
        total_value = sum(h.shares * h.current_price for h in portfolio.holdings)
        if total_value <= 0:
            raise ValueError("portfolio market value must be greater than zero")

        targets = cls.compute_target_allocation(ips)
        current_by_class = {asset_class: 0.0 for asset_class in targets}
        for holding in portfolio.holdings:
            current_by_class[holding.asset_class] += holding.shares * holding.current_price

        orders: list[TradeOrder] = []
        for holding in portfolio.holdings:
            current_value = holding.shares * holding.current_price
            class_current = current_by_class[holding.asset_class]
            class_target = total_value * targets[holding.asset_class]
            target_value = class_target * (current_value / class_current) if class_current else class_target
            difference = target_value - current_value
            if abs(difference) <= settings.trade_threshold_usd:
                continue

            shares = abs(difference) / holding.current_price if holding.current_price else 0
            action = "BUY" if difference > 0 else "SELL"
            gain_per_share = max(0.0, holding.current_price - holding.cost_basis)
            tax_impact = shares * gain_per_share * ips.tax_bracket_pct / 100 if action == "SELL" else 0.0
            orders.append(TradeOrder(
                symbol=holding.symbol,
                action=action,
                shares=round(shares, 6),
                estimated_price=holding.current_price,
                tax_impact_usd=round(tax_impact, 2),
                reasoning=f"Move {holding.asset_class} toward {targets[holding.asset_class]:.0%} policy target",
            ))
        return orders
