from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Holding(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(min_length=1, max_length=32)
    asset_class: Literal["Equity", "Fixed Income", "Commodity", "Cash"]
    shares: float = Field(ge=0)
    current_price: float = Field(ge=0)
    cost_basis: float = Field(ge=0)
    sector: str | None = None


class IPSProfile(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    client_id: str = Field(min_length=1)
    risk_score: int = Field(ge=1, le=10)
    time_horizon_years: int = Field(ge=0)
    liquidity_needs_usd: float = Field(ge=0)
    tax_bracket_pct: float = Field(ge=0, le=100)
    prohibited_sectors: list[str] = []


class Portfolio(BaseModel):
    client_id: str = Field(min_length=1)
    holdings: list[Holding] = Field(min_length=1)

    @field_validator("holdings")
    @classmethod
    def unique_symbols(cls, holdings: list[Holding]) -> list[Holding]:
        symbols = [holding.symbol for holding in holdings]
        if len(symbols) != len(set(symbols)):
            raise ValueError("holdings must contain unique symbols")
        return holdings


class TradeOrder(BaseModel):
    symbol: str
    action: Literal["BUY", "SELL", "HOLD"]
    shares: float = Field(ge=0)
    estimated_price: float = Field(ge=0)
    tax_impact_usd: float = Field(ge=0)
    reasoning: str


class RebalanceProposal(BaseModel):
    client_id: str
    target_allocations: dict[str, float]
    orders: list[TradeOrder]
    compliance_approved: bool
    violations: list[str] = []
    audit_id: str


class RebalanceRequest(BaseModel):
    ips: IPSProfile
    portfolio: Portfolio

    @model_validator(mode="after")
    def matching_client_ids(self) -> "RebalanceRequest":
        if self.ips.client_id != self.portfolio.client_id:
            raise ValueError("IPS and portfolio client_id values must match")
        return self
