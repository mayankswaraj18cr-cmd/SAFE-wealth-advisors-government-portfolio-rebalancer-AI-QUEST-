from config import settings
from models import IPSProfile, Portfolio, TradeOrder


class LyzrSafeAIGuard:
    @staticmethod
    def validate_suitability(ips: IPSProfile, orders: list[TradeOrder]) -> tuple[bool, list[str]]:
        violations: list[str] = []
        prohibited_sectors = {sector.casefold() for sector in ips.prohibited_sectors}

        for order in orders:
            if order.symbol in settings.prohibited_assets:
                violations.append(f"CRITICAL: {order.symbol} is on the prohibited asset list")
            if any(sector in order.reasoning.casefold() for sector in prohibited_sectors):
                violations.append(f"SUITABILITY: {order.symbol} matches a prohibited sector")
            if ips.risk_score <= 3 and order.action == "SELL" and order.tax_impact_usd > 5000:
                violations.append(f"TAX GUARD: {order.symbol} exceeds the conservative tax limit")

        return not violations, violations

    @staticmethod
    def validate_cash_buffer(portfolio: Portfolio) -> list[str]:
        total_value = sum(holding.shares * holding.current_price for holding in portfolio.holdings)
        cash_value = sum(
            holding.shares * holding.current_price
            for holding in portfolio.holdings
            if holding.asset_class == "Cash"
        )
        if total_value <= 0 or cash_value / total_value < settings.min_cash_buffer_pct:
            return [f"LIQUIDITY: portfolio must retain at least {settings.min_cash_buffer_pct:.0%} cash"]
        return []
