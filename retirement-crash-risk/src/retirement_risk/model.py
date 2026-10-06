from __future__ import annotations

import math

import pandas as pd


def period_return(series: pd.Series, start: str, end: str) -> float:
    """Return the price change between the closest available dates inside a window."""
    s = series.dropna().sort_index()
    if s.empty:
        return math.nan
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    inside = s.loc[(s.index >= start_ts) & (s.index <= end_ts)]
    if len(inside) < 2:
        return math.nan
    return float(inside.iloc[-1] / inside.iloc[0] - 1.0)


def calculate_scenario_returns(
    prices: pd.DataFrame, scenarios: dict[str, tuple[str, str]]
) -> pd.DataFrame:
    rows = []
    for scenario, (start, end) in scenarios.items():
        for ticker in prices.columns:
            rows.append(
                {
                    "scenario": scenario,
                    "ticker": ticker,
                    "return": period_return(prices[ticker], start, end),
                }
            )
    return pd.DataFrame(rows)


def blended_portfolio_return(equity_return: float, bond_return: float, equity_weight: float) -> float:
    bond_weight = 1.0 - equity_weight
    return equity_weight * equity_return + bond_weight * bond_return


def project_retirement_balance(
    age: int,
    salary: float,
    start_balance: float,
    equity_weight: float,
    employee_contribution: float,
    employer_match: float,
    retirement_age: int,
    salary_growth: float,
    expected_equity_return: float,
    expected_bond_return: float,
    initial_shock: float = 0.0,
) -> float:
    """Project an illustrative balance to retirement after an immediate market shock."""
    years = max(int(retirement_age - age), 0)
    balance = float(start_balance) * (1.0 + initial_shock)
    current_salary = float(salary)
    portfolio_return = (
        equity_weight * expected_equity_return
        + (1.0 - equity_weight) * expected_bond_return
    )

    for _ in range(years):
        contribution = current_salary * (employee_contribution + employer_match)
        # Contributions are treated as arriving through the year; half-year growth is a simple approximation.
        balance = balance * (1.0 + portfolio_return) + contribution * (1.0 + portfolio_return / 2.0)
        current_salary *= 1.0 + salary_growth
    return balance


def retirement_shortfall_pct(baseline: float, stressed: float) -> float:
    if baseline <= 0:
        return math.nan
    return stressed / baseline - 1.0
