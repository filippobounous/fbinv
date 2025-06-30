"""Analytics endpoints for calculating portfolio and security statistics."""

import pandas as pd
from fastapi import APIRouter

from investment.analytics.correlation import CorrelationCalculator
from investment.core.portfolio import Portfolio
from investment.core.security.generic import Generic
from investment.utils.consts import (
    DEFAULT_RET_WIN_SIZE,
    DEFAULT_CORR_MODEL,
    DEFAULT_RV_MODEL,
    DEFAULT_RV_WIN_SIZE,
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_CONFIDENCE_LEVEL,
    DEFAULT_VAR_MODEL,
    DEFAULT_METRIC_WIN_SIZE,
    DEFAULT_VAR_WIN_SIZE,
    TRADING_DAYS,
)

from .utils import EXPECTED_EXCEPTIONS

router = APIRouter(prefix="/analytics")

@router.post("/correlations")
async def calculate_correlations(
    portfolio_codes: list[str] | None = None,
    security_codes: list[str] | None = None,
    use_returns: bool = False,
    log_returns: bool = True,
    ret_win_size: int = DEFAULT_RET_WIN_SIZE,
    corr_model: str = DEFAULT_CORR_MODEL,
    window: int | None = None,
    lag: int = 0,
) -> dict:
    """Calculate correlation statistics for the given entities."""
    portfolios = [Portfolio(code) for code in (portfolio_codes or [])]
    securities = [Generic(code) for code in (security_codes or [])]

    calculator = CorrelationCalculator(
        securities=securities, portfolios=portfolios
    )
    result = calculator.calculate(
        use_returns=use_returns,
        log_returns=log_returns,
        ret_win_size=ret_win_size,
        corr_model=corr_model,
        window=window,
        lag=lag,
    )

    if isinstance(result, pd.DataFrame):
        return {"correlation_matrix": result.to_dict()}
    return {f"{k[0]}-{k[1]}": v.to_dict() for k, v in result.items()}

@router.post("/returns")
async def calculate_returns(
    portfolio_codes: list[str] | None = None,
    security_codes: list[str] | None = None,
    use_ln_ret: bool = True,
    win_size: int = DEFAULT_RET_WIN_SIZE,
    local_only: bool = True,
) -> dict[str, list[dict]]:
    """Calculate returns for the provided securities or portfolios."""
    results: dict[str, list[dict] | dict[str, str]] = {}

    portfolio_codes = portfolio_codes or []
    security_codes = security_codes or []

    for code in portfolio_codes:
        try:
            df = Portfolio(code).get_returns(
                use_ln_ret=use_ln_ret,
                ret_win_size=win_size,
                local_only=local_only,
            )
            results[code] = df.to_dict(orient="records")
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    for code in security_codes:
        try:
            df = Generic(code).get_returns(
                use_ln_ret=use_ln_ret,
                ret_win_size=win_size,
                local_only=local_only,
            )
            results[code] = df.to_dict(orient="records")
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    return results

@router.post("/prices")
async def get_prices(
    portfolio_codes: list[str] | None = None,
    security_codes: list[str] | None = None,
    local_only: bool = True,
    intraday: bool = False,
    currency: str | None = None,
) -> dict[str, list[dict]]:
    """Return price history for the provided entities."""
    results: dict[str, list[dict] | dict[str, str]] = {}

    portfolio_codes = portfolio_codes or []
    security_codes = security_codes or []

    for code in portfolio_codes:
        try:
            df = Portfolio(code).get_price_history(
                local_only=local_only,
                intraday=intraday,
                currency=currency,
            )
            results[code] = df.to_dict(orient="records")
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    for code in security_codes:
        try:
            df = Generic(code).get_price_history(
                local_only=local_only,
                intraday=intraday,
                currency=currency,
            )
            results[code] = df.to_dict(orient="records")
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    return results

@router.post("/realised-volatility")
async def calculate_realised_volatility(
    portfolio_codes: list[str] | None = None,
    security_codes: list[str] | None = None,
    rv_model: str = DEFAULT_RV_MODEL,
    rv_win_size: int = DEFAULT_RV_WIN_SIZE,
    local_only: bool = True,
) -> dict[str, list[dict]]:
    """Return realised volatility for the provided entities."""
    results: dict[str, list[dict] | dict[str, str]] = {}

    for code in portfolio_codes or []:
        try:
            df = Portfolio(code).get_realised_volatility(
                rv_model=rv_model,
                rv_win_size=rv_win_size,
                local_only=local_only,
            )
            results[code] = df.to_dict(orient="records")
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    for code in security_codes or []:
        try:
            df = Generic(code).get_realised_volatility(
                rv_model=rv_model,
                rv_win_size=rv_win_size,
                local_only=local_only,
            )
            results[code] = df.to_dict(orient="records")
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    return results

@router.post("/metrics")
async def get_metrics(
    portfolio_codes: list[str] | None = None,
    security_codes: list[str] | None = None,
    metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = TRADING_DAYS,
    local_only: bool = True,
) -> dict[str, dict[str, float]]:
    """Return performance metrics for the provided entities."""
    results: dict[str, dict[str, float] | dict[str, str]] = {}

    for code in portfolio_codes or []:
        try:
            metrics = Portfolio(code).get_performance_metrics(
                metric_win_size=metric_win_size,
                risk_free_rate=risk_free_rate,
                periods_per_year=periods_per_year,
                local_only=local_only,
            )
            results[code] = metrics
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    for code in security_codes or []:
        try:
            metrics = Generic(code).get_performance_metrics(
                metric_win_size=metric_win_size,
                risk_free_rate=risk_free_rate,
                periods_per_year=periods_per_year,
                local_only=local_only,
            )
            results[code] = metrics
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    return results

@router.post("/var")
async def get_value_at_risk(
    portfolio_codes: list[str] | None = None,
    security_codes: list[str] | None = None,
    var_win_size: int = DEFAULT_VAR_WIN_SIZE,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    method: str = DEFAULT_VAR_MODEL,
    local_only: bool = True,
) -> dict[str, float]:
    """Return Value-at-Risk for the provided entities."""
    results: dict[str, float | dict[str, str]] = {}

    for code in portfolio_codes or []:
        try:
            var_value = Portfolio(code).get_value_at_risk(
                var_win_size=var_win_size,
                confidence_level=confidence_level,
                method=method,
                local_only=local_only,
            )
            results[code] = var_value
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    for code in security_codes or []:
        try:
            var_value = Generic(code).get_value_at_risk(
                var_win_size=var_win_size,
                confidence_level=confidence_level,
                method=method,
                local_only=local_only,
            )
            results[code] = var_value
        except EXPECTED_EXCEPTIONS as exc:  # pragma: no cover - small wrapper
            results[code] = {"error": str(exc)}

    return results
