# Retirement Crash Risk

A reproducible Python project that stress-tests passively invested workplace retirement portfolios against major U.S. financial downturns and asks how vulnerability changes with worker age and sector exposure.

## Research question

**How vulnerable are passively invested workplace retirement portfolios to financial downturns, and how does that vulnerability vary across worker age and industry exposure?**

The first version of the project treats **sector exposure** as a transparent, reproducible proxy for broader industry exposure. It separates two questions:

1. **Lifecycle vulnerability:** How does the same market shock affect workers at different ages and distances from retirement?
2. **Sector concentration:** Which equity sectors contribute most to losses when today's broad-market exposure is subjected to historical sector shocks?

## Hypotheses

- **H1 — Lifecycle vulnerability:** Workers closer to retirement are more economically vulnerable to market downturns because they have less time for portfolio recovery and a larger share of lifetime retirement wealth already accumulated.
- **H2 — Technology concentration:** Information technology is a disproportionately important source of downside risk because of its large weight in broad U.S. equity portfolios and its sensitivity in some historical downturns.
- **H3 — Diversification limits:** Broad passive diversification reduces company-specific risk but does not eliminate large losses during market-wide stress.

These are hypotheses, not assumptions. The code is designed so the results can reject them.

## What the project does

The project creates four illustrative workers:

| Age | Career stage | Equity / bond allocation |
|---:|---|---:|
| 25 | Early career | 90 / 10 |
| 40 | Mid career | 80 / 20 |
| 55 | Late career | 60 / 40 |
| 64 | Near retirement | 40 / 60 |

It then replays four historical stress episodes:

- Dot-com bust: March 24, 2000 to October 9, 2002
- Global Financial Crisis: October 9, 2007 to March 9, 2009
- COVID-19 crash: February 19, 2020 to March 23, 2020
- 2022 tightening drawdown: January 3, 2022 to October 12, 2022

For each worker, the analysis estimates:

- immediate portfolio return during the stress period;
- immediate dollar change in the retirement account;
- projected retirement balance at age 65 under a no-crash baseline;
- projected retirement balance after the crash;
- the percentage shortfall at retirement caused by the crash.

It also compares fixed 100/0, 80/20, 60/40, and 40/60 stock/bond portfolios and estimates sector-level contribution to historical equity stress.

## Languages and tools

- **Python 3.11+** — analysis language
- **pandas** — tabular data manipulation
- **NumPy** — numerical operations
- **Matplotlib** — figures
- **yfinance** — public market-data retrieval without an API key
- **pytest** — automated tests
- **GitHub Actions** — runs the tests automatically after code is pushed to GitHub

## Data sources

The project is intentionally designed to run without paid APIs.

### Market returns

Historical prices are downloaded through the `yfinance` Python package from Yahoo Finance.

The broad-asset proxies are:

- `VFINX` — Vanguard 500 Index Fund Investor Shares, used as the long-history U.S. equity proxy
- `VBMFX` — Vanguard Total Bond Market Index Fund Investor Shares, used as the long-history U.S. bond proxy

These long-history fund proxies allow the same stock/bond framework to cover the dot-com bust, the Global Financial Crisis, the COVID-19 crash, and the 2022 drawdown.

### Sector returns

Sector shocks use exchange-traded fund proxies such as:

- `XLK` — Information Technology
- `XLF` — Financials
- `XLY` — Consumer Discretionary
- `XLV` — Health Care
- `XLI` — Industrials
- `XLP` — Consumer Staples
- `XLE` — Energy
- `XLU` — Utilities
- `XLB` — Materials
- `XLRE` — Real Estate
- `XLC` — Communication Services

Some sector ETFs did not exist during older crises. When a sector lacks valid history for a stress window, the sector-attribution calculation excludes it for that scenario and renormalizes the remaining weights. The output records this explicitly.

### Current sector weights

The project attempts to retrieve current SPY sector weights through `yfinance` fund data. If that live request fails, it falls back to `data/illustrative_sector_weights.csv` so the project remains runnable. The output identifies which source was used.

### Worker assumptions

The four worker profiles in `data/worker_profiles.csv` are **illustrative scenarios, not estimates of the average American worker**. Salary, starting balance, contribution rate, employer match, and asset allocation are editable inputs.

## How to run the project — plain-English version

You do not need to be an experienced programmer. You need Python installed and an internet connection for the market-data download.

### 1. Download the project

On GitHub, click **Code**, then **Download ZIP**. Unzip the folder somewhere easy to find, such as your Desktop.

If you use Git, you can instead clone the repository normally.

### 2. Open a terminal in the project folder

On macOS, open Terminal and move into the folder. For example:

```bash
cd ~/Desktop/retirement-crash-risk
```

On Windows, open PowerShell in the folder.

### 3. Create a private Python environment

This keeps the project's packages separate from the rest of your computer.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install the packages

```bash
pip install -r requirements.txt
```

You only need to do this the first time, unless the package list changes.

### 5. Run the analysis

```bash
python run_analysis.py
```

The program will download the required historical market data, run every stress test, and save the results in the `outputs` folder.

### 6. Look at the results

After the program finishes, open:

- `outputs/worker_stress_results.csv` — age-by-crash results
- `outputs/synthetic_portfolio_results.csv` — fixed stock/bond portfolio comparison
- `outputs/sector_attribution.csv` — which sectors contributed most to each historical shock
- `outputs/sector_weights_used.csv` — the sector weights used in the analysis
- `outputs/figures/` — charts generated by the project

A `.csv` file can be opened in Excel, Google Sheets, Numbers, or any text editor.

### 7. Run the tests

This step checks that the core calculations behave as expected:

```bash
pytest -q
```

If you see all tests passing, the main model functions are behaving as designed.

## Changing the assumptions

Most assumptions can be changed without editing Python code.

### Change the workers

Open `data/worker_profiles.csv` in Excel, Numbers, or a text editor. You can change:

- age;
- salary;
- current retirement-account balance;
- stock allocation;
- employee contribution rate;
- employer match.

Save the file and run:

```bash
python run_analysis.py
```

### Change the market assumptions

Expected post-crash stock returns, bond returns, salary growth, retirement age, historical stress windows, and ticker mappings are stored in:

`src/retirement_risk/settings.py`

## Repository structure

```text
retirement-crash-risk/
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/
│   ├── illustrative_sector_weights.csv
│   └── worker_profiles.csv
├── outputs/
│   └── figures/
├── src/
│   └── retirement_risk/
│       ├── __init__.py
│       ├── analysis.py
│       ├── data.py
│       ├── model.py
│       └── settings.py
├── tests/
│   └── test_model.py
├── .gitignore
├── LICENSE
├── METHODOLOGY.md
├── README.md
├── requirements.txt
└── run_analysis.py
```

## Interpreting the results carefully

This is a stress-testing project, not a forecast and not financial advice.

A few distinctions matter:

- A 401(k) or similar workplace account is an account structure, not an asset class. Risk comes from the investments held inside it.
- The four workers are scenarios, not population estimates.
- The sector analysis asks what would happen if **today's broad-market sector mix** encountered historical sector shocks. It does not claim to reconstruct the exact S&P 500 sector weights or the exact holdings of every retirement fund in each historical crisis.
- The post-crash retirement projection uses simple constant expected returns. It is intended to isolate lifecycle effects, not predict a worker's actual retirement wealth.
- Historical stress does not describe every possible future crisis.

See `METHODOLOGY.md` for the full modeling logic and limitations.

## Possible extensions

Good follow-on versions could add:

- Monte Carlo or block-bootstrap return simulations;
- target-date funds using actual published glide paths;
- inflation-adjusted retirement income replacement ratios;
- contribution interruptions during recessions;
- household-level retirement data from the Federal Reserve Survey of Consumer Finances;
- international equity exposure;
- deeper industry-level holdings analysis rather than sector-level proxies;
- factor exposures and correlations during stress regimes;
- sensitivity analysis around retirement age and withdrawal timing.

## Why this project exists

Passive retirement investing can diversify individual-company risk, but workers still bear market risk through their retirement accounts. This project makes that exposure measurable and asks whether the consequences differ systematically across the worker lifecycle and across sectors of the market.

## License

MIT License. See `LICENSE`.
