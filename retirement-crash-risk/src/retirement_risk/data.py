from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from .settings import BENCHMARK_TICKER, YF_SECTOR_NAME_MAP


def _require_yfinance():
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError(
            "yfinance is not installed. Run: pip install -r requirements.txt"
        ) from exc
    return yf


def download_adjusted_prices(
    tickers: Iterable[str], start: str = "1998-12-01", end: str = "2023-01-15"
) -> pd.DataFrame:
    """Download adjusted daily prices from Yahoo Finance via yfinance."""
    yf = _require_yfinance()
    tickers = list(dict.fromkeys(tickers))
    raw = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=False,
    )
    if raw.empty:
        raise RuntimeError("No market data were returned by Yahoo Finance.")

    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" not in raw.columns.get_level_values(0):
            raise RuntimeError("Expected a Close field in downloaded market data.")
        prices = raw["Close"].copy()
    else:
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})

    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    prices.index = pd.to_datetime(prices.index)
    prices = prices.sort_index()
    return prices


def get_spy_sector_weights(fallback_csv: Path) -> tuple[pd.Series, str]:
    """Fetch current SPY sector weights; fall back to an illustrative local file."""
    yf = _require_yfinance()
    try:
        raw = yf.Ticker(BENCHMARK_TICKER).funds_data.sector_weightings
        if not raw:
            raise ValueError("Empty sector weights")

        normalized: dict[str, float] = {}
        for key, value in raw.items():
            clean_key = str(key).strip().lower().replace("_", "-").replace(" ", "-")
            sector = YF_SECTOR_NAME_MAP.get(clean_key)
            if sector is not None and value is not None:
                normalized[sector] = float(value)

        series = pd.Series(normalized, dtype=float)
        if len(series) < 8 or series.sum() <= 0:
            raise ValueError("Sector weight response was incomplete")
        series = series / series.sum()
        return series.sort_values(ascending=False), "live SPY sector weights from Yahoo Finance"
    except Exception:
        fallback = pd.read_csv(fallback_csv)
        series = fallback.set_index("sector")["weight"].astype(float)
        series = series / series.sum()
        return series.sort_values(ascending=False), "illustrative local fallback weights"


def load_worker_profiles(path: Path) -> pd.DataFrame:
    workers = pd.read_csv(path)
    required = {
        "age",
        "label",
        "salary",
        "start_balance",
        "equity_weight",
        "employee_contribution",
        "employer_match",
    }
    missing = required.difference(workers.columns)
    if missing:
        raise ValueError(f"Worker profile file is missing columns: {sorted(missing)}")
    return workers
