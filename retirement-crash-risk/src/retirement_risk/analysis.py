from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data import download_adjusted_prices, get_spy_sector_weights, load_worker_profiles
from .model import (
    blended_portfolio_return,
    calculate_scenario_returns,
    project_retirement_balance,
    retirement_shortfall_pct,
)
from .settings import (
    BOND_TICKER,
    EQUITY_TICKER,
    EXPECTED_BOND_RETURN,
    EXPECTED_EQUITY_RETURN,
    RETIREMENT_AGE,
    SALARY_GROWTH,
    SCENARIOS,
    SECTOR_TICKERS,
    SYNTHETIC_PORTFOLIOS,
)


def _scenario_lookup(returns: pd.DataFrame, scenario: str, ticker: str) -> float:
    match = returns.loc[
        (returns["scenario"] == scenario) & (returns["ticker"] == ticker), "return"
    ]
    return float(match.iloc[0]) if len(match) else np.nan


def build_worker_stress_table(
    workers: pd.DataFrame, scenario_returns: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    for _, worker in workers.iterrows():
        baseline = project_retirement_balance(
            age=int(worker.age),
            salary=float(worker.salary),
            start_balance=float(worker.start_balance),
            equity_weight=float(worker.equity_weight),
            employee_contribution=float(worker.employee_contribution),
            employer_match=float(worker.employer_match),
            retirement_age=RETIREMENT_AGE,
            salary_growth=SALARY_GROWTH,
            expected_equity_return=EXPECTED_EQUITY_RETURN,
            expected_bond_return=EXPECTED_BOND_RETURN,
            initial_shock=0.0,
        )
        for scenario in SCENARIOS:
            eq = _scenario_lookup(scenario_returns, scenario, EQUITY_TICKER)
            bd = _scenario_lookup(scenario_returns, scenario, BOND_TICKER)
            shock = blended_portfolio_return(eq, bd, float(worker.equity_weight))
            stressed = project_retirement_balance(
                age=int(worker.age),
                salary=float(worker.salary),
                start_balance=float(worker.start_balance),
                equity_weight=float(worker.equity_weight),
                employee_contribution=float(worker.employee_contribution),
                employer_match=float(worker.employer_match),
                retirement_age=RETIREMENT_AGE,
                salary_growth=SALARY_GROWTH,
                expected_equity_return=EXPECTED_EQUITY_RETURN,
                expected_bond_return=EXPECTED_BOND_RETURN,
                initial_shock=shock,
            )
            rows.append(
                {
                    "age": int(worker.age),
                    "worker": worker.label,
                    "scenario": scenario,
                    "equity_weight": float(worker.equity_weight),
                    "immediate_return": shock,
                    "immediate_dollar_change": float(worker.start_balance) * shock,
                    "years_to_retirement": max(RETIREMENT_AGE - int(worker.age), 0),
                    "baseline_balance_at_65": baseline,
                    "stressed_balance_at_65": stressed,
                    "retirement_balance_shortfall_pct": retirement_shortfall_pct(baseline, stressed),
                }
            )
    return pd.DataFrame(rows)


def build_synthetic_portfolio_table(scenario_returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        eq = _scenario_lookup(scenario_returns, scenario, EQUITY_TICKER)
        bd = _scenario_lookup(scenario_returns, scenario, BOND_TICKER)
        for portfolio, eq_weight in SYNTHETIC_PORTFOLIOS.items():
            rows.append(
                {
                    "scenario": scenario,
                    "portfolio": portfolio,
                    "equity_weight": eq_weight,
                    "return": blended_portfolio_return(eq, bd, eq_weight),
                }
            )
    return pd.DataFrame(rows)


def build_sector_attribution(
    scenario_returns: pd.DataFrame, sector_weights: pd.Series
) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        available = []
        for sector, ticker in SECTOR_TICKERS.items():
            ret = _scenario_lookup(scenario_returns, scenario, ticker)
            if pd.notna(ret) and sector in sector_weights.index:
                available.append((sector, ticker, float(ret), float(sector_weights.loc[sector])))

        total_weight = sum(x[3] for x in available)
        if total_weight <= 0:
            continue

        for sector, ticker, ret, raw_weight in available:
            weight = raw_weight / total_weight
            rows.append(
                {
                    "scenario": scenario,
                    "sector": sector,
                    "ticker": ticker,
                    "raw_current_weight": raw_weight,
                    "renormalized_weight": weight,
                    "historical_sector_return": ret,
                    "weighted_contribution": weight * ret,
                }
            )
    result = pd.DataFrame(rows)
    if not result.empty:
        result["downside_rank"] = result.groupby("scenario")["weighted_contribution"].rank(
            method="min", ascending=True
        )
        result["technology_largest_negative_contributor"] = False
        for _, group in result.groupby("scenario"):
            worst_idx = group["weighted_contribution"].idxmin()
            if result.loc[worst_idx, "sector"] == "Information Technology":
                result.loc[worst_idx, "technology_largest_negative_contributor"] = True
    return result


def save_figures(worker_table: pd.DataFrame, sector_table: pd.DataFrame, figure_dir: Path) -> None:
    figure_dir.mkdir(parents=True, exist_ok=True)

    pivot = worker_table.pivot(index="scenario", columns="worker", values="immediate_return") * 100
    ax = pivot.plot(kind="bar", figsize=(11, 6))
    ax.set_title("Immediate portfolio return under historical stress scenarios")
    ax.set_ylabel("Return (%)")
    ax.set_xlabel("")
    ax.axhline(0, linewidth=0.8)
    ax.legend(title="Illustrative worker")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(figure_dir / "worker_stress_returns.png", dpi=180)
    plt.close()

    shortfall = worker_table.pivot(
        index="scenario", columns="worker", values="retirement_balance_shortfall_pct"
    ) * 100
    ax = shortfall.plot(kind="bar", figsize=(11, 6))
    ax.set_title("Projected retirement-balance shortfall caused by an immediate crash")
    ax.set_ylabel("Difference vs. no-crash baseline at age 65 (%)")
    ax.set_xlabel("")
    ax.axhline(0, linewidth=0.8)
    ax.legend(title="Illustrative worker")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(figure_dir / "retirement_shortfall.png", dpi=180)
    plt.close()

    if not sector_table.empty:
        tech = sector_table[sector_table["sector"] == "Information Technology"].copy()
        tech["weighted_contribution_pct"] = tech["weighted_contribution"] * 100
        ax = tech.plot(
            x="scenario",
            y="weighted_contribution_pct",
            kind="bar",
            legend=False,
            figsize=(10, 5),
        )
        ax.set_title("Technology contribution to equity stress using current broad-market weights")
        ax.set_ylabel("Weighted contribution (percentage points)")
        ax.set_xlabel("")
        ax.axhline(0, linewidth=0.8)
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        plt.savefig(figure_dir / "technology_contribution.png", dpi=180)
        plt.close()


def run_project(root: Path) -> dict[str, Path | str]:
    data_dir = root / "data"
    output_dir = root / "outputs"
    figure_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    workers = load_worker_profiles(data_dir / "worker_profiles.csv")
    all_tickers = [EQUITY_TICKER, BOND_TICKER, *SECTOR_TICKERS.values()]
    prices = download_adjusted_prices(all_tickers)
    scenario_returns = calculate_scenario_returns(prices, SCENARIOS)
    sector_weights, weight_source = get_spy_sector_weights(
        data_dir / "illustrative_sector_weights.csv"
    )

    worker_table = build_worker_stress_table(workers, scenario_returns)
    portfolio_table = build_synthetic_portfolio_table(scenario_returns)
    sector_table = build_sector_attribution(scenario_returns, sector_weights)

    paths = {
        "scenario_returns": output_dir / "scenario_asset_returns.csv",
        "worker_stress": output_dir / "worker_stress_results.csv",
        "synthetic_portfolios": output_dir / "synthetic_portfolio_results.csv",
        "sector_attribution": output_dir / "sector_attribution.csv",
        "sector_weights": output_dir / "sector_weights_used.csv",
    }
    scenario_returns.to_csv(paths["scenario_returns"], index=False)
    worker_table.to_csv(paths["worker_stress"], index=False)
    portfolio_table.to_csv(paths["synthetic_portfolios"], index=False)
    sector_table.to_csv(paths["sector_attribution"], index=False)
    sector_weights.rename("weight").to_csv(paths["sector_weights"])

    save_figures(worker_table, sector_table, figure_dir)
    return {**paths, "sector_weight_source": weight_source}
