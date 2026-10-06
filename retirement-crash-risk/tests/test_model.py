import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from retirement_risk.model import (
    blended_portfolio_return,
    period_return,
    project_retirement_balance,
    retirement_shortfall_pct,
)


def test_period_return_uses_inside_window():
    s = pd.Series(
        [100.0, 90.0, 80.0],
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    assert period_return(s, "2020-01-01", "2020-01-03") == pytest.approx(-0.20)


def test_blended_portfolio_return():
    got = blended_portfolio_return(-0.40, 0.10, 0.60)
    assert round(got, 6) == -0.20


def test_crash_lowers_terminal_balance():
    common = dict(
        age=55,
        salary=100000,
        start_balance=500000,
        equity_weight=0.60,
        employee_contribution=0.10,
        employer_match=0.04,
        retirement_age=65,
        salary_growth=0.03,
        expected_equity_return=0.06,
        expected_bond_return=0.03,
    )
    baseline = project_retirement_balance(**common, initial_shock=0.0)
    stressed = project_retirement_balance(**common, initial_shock=-0.20)
    assert stressed < baseline
    assert retirement_shortfall_pct(baseline, stressed) < 0
