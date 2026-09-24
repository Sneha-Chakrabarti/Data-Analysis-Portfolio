# NSE Electronic Gold Receipt (EGR) Price and Liquidity Analysis

Analysis of daily trading data for GOLD10G99, an Electronic Gold Receipt
(EGR) listed on the NSE, covering 17 August 2026 to 11 September 2026 (20
trading days).

## Background

An Electronic Gold Receipt is a SEBI-regulated instrument that lets gold
be traded on the exchange in dematerialized form, backed by physical gold
held in accredited vaults, and convertible back into physical gold. It
trades like a regular security (own order book, daily OHLC, traded
volume) rather than being a derivative or a mutual fund unit. GOLD10G99
represents a 10 gram, 99.9 percent purity gold receipt.

## What this project shows

- Cleaning a real NSE export: Indian-style numbering (lakh commas, e.g.
  "1,58,982.00") in every numeric column, and dates listed newest-first
- Computing return and volatility for a short window honestly, without
  overstating what 20 days of data can support
- Basic liquidity analysis: traded value, trade count, average trade size
- Working with an underlying-commodity-backed instrument rather than an
  equity, so returns move with domestic gold prices rather than company
  fundamentals

## Data source

NSE's EGR historical data archive:
https://www.nseindia.com/historical-data/egr. The uploaded export
(`data/EGR-Historical--15-08-2026-15-09-2026.csv`) covers 17-Aug-2026 to
11-Sep-2026 for GOLD10G99.

## Repository structure

```
nse-egr-analysis/
  config.py            file paths, symbol
  clean_data.py         parses the raw NSE export, fixes number formatting
  analyze.py             returns, volatility, liquidity metrics
  visualize.py            generates the figures below
  requirements.txt
  data/                  raw NSE export, as downloaded
  output/                cleaned data, computed CSVs, figures
```

## Setup

```bash
git clone <your-repo-url>
cd nse-egr-analysis
pip install -r requirements.txt
```

## Usage

```bash
python clean_data.py    # writes output/egr_cleaned.csv
python analyze.py       # writes output/egr_analysis.csv, prints summary
python visualize.py     # writes output/figures/*.png
```

## Methodology

    DailyReturn    = pct change in Close Price day over day
    DailyRange     = High Price - Low Price
    DailyRangePct  = DailyRange / Open Price
    AvgTradeSize   = Value / No. Of Trades

Annualized volatility is computed as daily standard deviation of returns
times the square root of 252, labeled "naive" throughout because 20 days
is a small sample; it is included to show the calculation, not as a
reliable long-run estimate.

## Results

- **Period**: 17 Aug 2026 to 11 Sep 2026 (20 trading days)
- **Close price**: Rs 158,961 to Rs 156,897 per 10g unit, a **-1.30
  percent** move over the window
- **Peak close**: Rs 167,173 on 25 Aug 2026; **trough close**: Rs 155,334
  on 2 Sep 2026, a swing of roughly 7.6 percent within the month
- **Daily volatility**: 1.53 percent; naive annualized volatility (20-day
  sample) 24.2 percent
- **Liquidity**: averaged 129 units and 51 trades per day, Rs 2.07 crore
  in daily traded value, with an average trade size of roughly Rs 4.04
  lakh

See `output/figures/`:
1. `price_trend.png`: close price over the period, showing a run-up
   through late August followed by a sharp pullback in early September
2. `daily_returns.png`: day-by-day percentage returns, green/red coded
3. `liquidity.png`: traded quantity (bars) against traded value (line) on
   a shared timeline

## Limitations

- 20 trading days is too short to draw conclusions about EGR as an asset
  class; this is a snapshot, not a backtest
- Single symbol only (GOLD10G99); no comparison against a second EGR
  contract or against physical/international gold benchmarks
- No adjustment for the underlying international gold price or INR/USD
  movement, both of which likely explain most of the price action here

## Possible extensions

- Pull international spot gold (XAU/USD) and USD/INR over the same
  window and decompose EGR's move into gold-price effect vs currency
  effect
- Extend the date range as more monthly exports become available, to
  build a longer time series
- Compare EGR liquidity against gold ETFs listed on NSE for the same
  period

## License

MIT
