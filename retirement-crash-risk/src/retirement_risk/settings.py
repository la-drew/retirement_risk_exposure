from __future__ import annotations

from collections import OrderedDict

RETIREMENT_AGE = 65
SALARY_GROWTH = 0.03
EXPECTED_EQUITY_RETURN = 0.06
EXPECTED_BOND_RETURN = 0.03

# Broad asset proxies with long histories that cover all four stress windows.
EQUITY_TICKER = "VFINX"
BOND_TICKER = "VBMFX"
BENCHMARK_TICKER = "SPY"

# Current S&P 500 sector weights are fetched from SPY when possible.
# ETF proxies provide sector returns for historical stress windows.
SECTOR_TICKERS = OrderedDict(
    [
        ("Information Technology", "XLK"),
        ("Financials", "XLF"),
        ("Consumer Discretionary", "XLY"),
        ("Communication Services", "XLC"),
        ("Health Care", "XLV"),
        ("Industrials", "XLI"),
        ("Consumer Staples", "XLP"),
        ("Energy", "XLE"),
        ("Utilities", "XLU"),
        ("Real Estate", "XLRE"),
        ("Materials", "XLB"),
    ]
)

# Peak-to-trough windows chosen to represent major U.S. equity stress episodes.
SCENARIOS = OrderedDict(
    [
        ("Dot-com bust", ("2000-03-24", "2002-10-09")),
        ("Global Financial Crisis", ("2007-10-09", "2009-03-09")),
        ("COVID-19 crash", ("2020-02-19", "2020-03-23")),
        ("2022 tightening", ("2022-01-03", "2022-10-12")),
    ]
)

SYNTHETIC_PORTFOLIOS = OrderedDict(
    [
        ("100/0 equity/bond", 1.00),
        ("80/20 equity/bond", 0.80),
        ("60/40 equity/bond", 0.60),
        ("40/60 equity/bond", 0.40),
    ]
)

YF_SECTOR_NAME_MAP = {
    "basic-materials": "Materials",
    "communication-services": "Communication Services",
    "consumer-cyclical": "Consumer Discretionary",
    "consumer-defensive": "Consumer Staples",
    "energy": "Energy",
    "financial-services": "Financials",
    "healthcare": "Health Care",
    "industrials": "Industrials",
    "real-estate": "Real Estate",
    "technology": "Information Technology",
    "utilities": "Utilities",
}
