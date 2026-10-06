# Methodology

## 1. Objective

The project measures two related forms of vulnerability in passively invested workplace retirement portfolios:

1. **lifecycle vulnerability** — whether the consequences of a downturn differ by worker age and retirement horizon; and
2. **sector vulnerability** — whether broad-market passive equity exposure is especially sensitive to shocks in particular sectors.

The goal is stress testing, not forecasting.

## 2. Research question

> How vulnerable are passively invested workplace retirement portfolios to financial downturns, and how does that vulnerability vary across worker age and industry exposure?

In version 1, sector exposure is used as the reproducible proxy for industry exposure.

## 3. Hypotheses

### H1 — Lifecycle vulnerability

Workers close to retirement will experience greater economic damage from a severe market downturn because they have less time for subsequent contributions and compounding to dilute the effect of the initial loss.

### H2 — Technology concentration

Information technology will be one of the largest negative contributors to broad-equity stress because of its large current index weight and its sensitivity during certain crash regimes.

### H3 — Diversification limits

Passive diversification will reduce idiosyncratic risk but will not prevent substantial losses during systemic market stress.

## 4. Worker scenarios

The default file `data/worker_profiles.csv` defines four illustrative workers aged 25, 40, 55, and 64.

The profiles differ in:

- salary;
- starting retirement-account balance;
- equity allocation;
- years remaining to age 65.

All default workers contribute 10% of salary and receive a 4% employer contribution. These values are assumptions chosen to create interpretable scenarios, not claims about national averages.

## 5. Asset allocation

The default age-based allocations are deliberately simple:

- age 25: 90% equity / 10% bond;
- age 40: 80% equity / 20% bond;
- age 55: 60% equity / 40% bond;
- age 64: 40% equity / 60% bond.

The analysis also evaluates fixed 100/0, 80/20, 60/40, and 40/60 allocations so the effect of age can be distinguished from the effect of portfolio composition.

## 6. Stress windows

Four historical peak-to-trough windows are used:

| Scenario | Start | End |
|---|---|---|
| Dot-com bust | 2000-03-24 | 2002-10-09 |
| Global Financial Crisis | 2007-10-09 | 2009-03-09 |
| COVID-19 crash | 2020-02-19 | 2020-03-23 |
| 2022 tightening | 2022-01-03 | 2022-10-12 |

Returns are calculated from the first available trading-day observation on or after the stated start date to the last available observation on or before the stated end date.

## 7. Broad asset return calculation

Let:

- `r_e` = equity return during a stress window;
- `r_b` = bond return during the same window;
- `w_e` = portfolio equity weight.

The simple buy-and-hold stress return is:

```text
portfolio return = w_e * r_e + (1 - w_e) * r_b
```

The model does not rebalance inside the crash window. This keeps the calculation transparent and treats each scenario as a discrete stress shock.

## 8. Retirement-horizon projection

The project then asks how much an immediate crash changes the worker's projected balance at age 65.

For each worker, it computes two paths:

- **baseline:** no immediate shock;
- **stressed:** the historical portfolio shock occurs immediately.

After the initial shock, both paths use the same simplified annual assumptions:

- 6% expected nominal equity return;
- 3% expected nominal bond return;
- 3% annual salary growth;
- continued worker and employer contributions.

The annual portfolio return is:

```text
expected portfolio return
= equity weight * expected equity return
+ bond weight * expected bond return
```

The principal lifecycle metric is:

```text
retirement balance shortfall
= stressed balance at 65 / baseline balance at 65 - 1
```

Because both paths use identical assumptions after the initial crash, this metric isolates the long-run effect of the stress shock under the stated assumptions.

## 9. Sector attribution

The project attempts to retrieve current SPY sector weights. Each historical sector ETF return is combined with the current broad-market weight:

```text
weighted sector contribution
= current sector weight * historical sector return
```

This answers a counterfactual question:

> If today's broad-market sector mix were exposed to a historical crash regime, which sectors would contribute most to the loss?

It is intentionally **not** a reconstruction of historical sector weights.

### Missing historical sector ETFs

Communication Services (`XLC`) and Real Estate (`XLRE`) do not have the same long return history as the legacy Select Sector SPDR ETFs. If a sector does not have sufficient observations in a given scenario, that sector is omitted and the weights of available sectors are renormalized to sum to 100% for that scenario.

This is preferable to inventing unavailable return data.

## 10. Technology hypothesis test

For each scenario, the code ranks sectors by weighted contribution. The technology hypothesis is supported for a scenario when Information Technology has the most negative weighted contribution among sectors with valid return history.

The expected outcome is not hard-coded. Technology can rank first, second, or lower depending on the historical stress regime and the current sector weight.

## 11. Data limitations

### Market-data source

Yahoo Finance data accessed through `yfinance` are convenient and reproducible without credentials, but they are not an institutional-grade market-data feed.

### Fund proxies

`VFINX` and `VBMFX` are long-history mutual fund proxies for broad U.S. equities and bonds. They are not meant to represent every workplace retirement plan.

### Current versus historical exposure

Current SPY sector weights are deliberately applied to historical sector returns. The analysis therefore measures **current composition under historical shocks**, not the exact portfolio held by workers in 2000, 2008, 2020, or 2022.

### Worker profiles

The worker assumptions are illustrative. They do not use individual administrative retirement-account records.

### Constant post-crash expected returns

The retirement projection is deterministic after the initial shock. It does not model sequence-of-returns uncertainty, time-varying correlations, layoffs, contribution changes, taxes, withdrawals, inflation, or behavioral responses.

## 12. Interpretation

The cleanest interpretation is comparative:

- Which age profile experiences the largest immediate dollar loss?
- Which age profile retains the largest retirement-horizon shortfall?
- How much does de-risking toward bonds reduce historical stress losses?
- Which current sectors produce the largest weighted downside contribution under each historical scenario?
- Is technology consistently the dominant source of risk, or only in particular regimes?

These comparisons are more defensible than treating the model as a forecast of actual retirement outcomes.
