from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Safe Wealth Advisory & Governed Rebalancer"
    environment: str = "development"
    aims_endpoint: str | None = None
    lyzr_api_key: str | None = None
    min_cash_buffer_pct: float = Field(default=0.05, ge=0, le=1)
    trade_threshold_usd: float = Field(default=500.0, ge=0)
    conservative_max_equity_pct: float = Field(default=0.30, ge=0, le=1)
    prohibited_assets: list[str] = ["MEME_COIN", "UNCOVERED_OPTION", "HIGH_LEVERAGE_ETF"]


settings = Settings()
