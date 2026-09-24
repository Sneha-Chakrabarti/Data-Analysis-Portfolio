# ITC 5-Year Price, Trend and Delivery Analysis

Analysis of 5 years of daily trading data for ITC Ltd on the NSE, from 15
September 2021 to 15 September 2026 (1,253 trading days): price trend,
moving-average crossovers, drawdown, and delivery percentage (the share
of traded volume that settled by actual delivery rather than intraday
squaring-off, an NSE-specific signal of genuine investment demand versus
speculative trading).

## What this project shows

- Cleaning a real 5-year NSE export: padded column headers, Indian-style
  number formatting, and a small number of missing-data rows handled
  explicitly rather than silently dropped
- Standard technical analysis (50/200-day moving averages, golden and
  death cross detection, drawdown from peak)
- A less commonly used NSE-specific metric (delivery percentage) used
  correctly, not just plotted
- A clear, specific narrative built from the numbers: this stock roughly
  doubled, then gave back more than half its gains, over five years

## Data source

NSE Security-wise Price Volume Archives:
https://www.nseindia.com/report-detail/eq_security. The uploaded export
(`data/15-09-2021-TO-15-09-2026-ITC-ALL-N.csv`) covers ITC (series EQ)
from 15-Sep-2021 to 15-Sep-2026.

## Repository structure

```
nse-itc-analysis/
  config.py            file paths, symbol, moving-average windows
  clean_data.py         parses the raw export, fixes formatting and headers
  analyze.py             returns, moving averages, drawdown, yearly summary
  visualize.py            generates the figures below
  requirements.txt
  data/                  raw NSE export, as downloaded
  output/                cleaned data, computed CSVs, figures
```

## Setup

```bash
git clone <your-repo-url>
cd nse-itc-analysis
pip install -r requirements.txt
```

## Usage

```bash
python clean_data.py    # writes output/itc_cleaned.csv
python analyze.py       # writes output/itc_analysis.csv, output/yearly_summary.csv
python visualize.py     # writes output/figures/*.png
```

## Methodology

    DailyReturn  = pct change in Close Price day over day
    SMA50, SMA200 = 50-day and 200-day simple moving averages of Close Price
    Drawdown      = Close Price / running maximum Close Price - 1
    CAGR          = (End Price / Start Price)^(365.25 / days) - 1

**Golden cross**: the day the 50-day SMA crosses from at-or-below the
200-day SMA to above it, a traditional bullish signal. **Death cross**:
the mirror case, a traditional bearish signal.

**Delivery percentage** (`% Dly Qt to Traded Qty`, published directly by
NSE) is the fraction of a day's traded volume that resulted in actual
share delivery rather than being squared off intraday. A sustained high
delivery percentage suggests buying and holding rather than day trading;
a low one suggests speculative churn.

## Results

- **Period**: 15 Sep 2021 to 15 Sep 2026 (1,253 trading days)
- **Close price**: Rs 216.00 to Rs 258.00, **+19.4% total return, +3.6%
  CAGR** over the full 5 years
- **Peak close**: Rs 522.75 on 26 Sep 2024. From that peak, the stock has
  fallen to the current price, a **maximum drawdown of -51.1%** (trough
  on 31 Aug 2026 at Rs 255.50)
- **Annualized volatility**: 20.6%
- **Average delivery percentage**: 58.6% across the full period, and
  trending up in the back half of the window, consistent with the
  decline being driven by long-term holders reducing positions rather
  than pure speculative selling
- **Only one golden cross** in five years (23 Jul 2024, at Rs 492) and
  **two death crosses** (23 Feb 2024 at Rs 411, and 20 Jan 2025 at Rs
  438). The single golden cross occurred just two months before the
  all-time peak in this dataset and was reversed within six months.

**Year-by-year return**:

| Year | Return | Avg Delivery % |
|------|--------|-----------------|
| 2021 (partial) | +0.9% | 46.0% |
| 2022 | +51.3% | 55.8% |
| 2023 | +38.8% | 58.7% |
| 2024 | +3.3% | 58.4% |
| 2025 | -16.7% | 65.4% |
| 2026 (partial, thru Sep) | -29.1% | 58.4% |

The story in one line: ITC had two very strong years (2022, 2023), a
flat 2024 that masked a sharp intra-year reversal after the September
peak, and two consecutive down years since, giving back most of the
2022-2023 gains.

See `output/figures/`:
1. `price_with_moving_averages.png`: close price with 50/200-day SMAs and
   cross points marked
2. `drawdown.png`: drawdown from running peak across the full period
3. `delivery_percentage.png`: daily and 20-day rolling delivery
   percentage
4. `volume.png`: daily traded volume

## Limitations

- Moving-average crossovers and delivery percentage are descriptive here,
  not backtested as a trading strategy; no claim is made that acting on
  the golden/death cross signals would have been profitable
- No adjustment for corporate actions (ITC has had demergers and bonus
  issues in this window); a close-price series alone does not separate
  a genuine price decline from an adjustment-driven one, and the -51%
  drawdown figure should be read with that caveat
- Single stock only, no sector or index benchmark to contextualize
  whether this move was ITC-specific or market-wide

## Possible extensions

- Overlay the Nifty FMCG index or Nifty50 over the same window to see
  how much of the decline was stock-specific versus sector-wide
- Check NSE/BSE corporate action filings for ITC over this period and
  adjust the price series accordingly
- Backtest the golden/death cross signal properly (entry/exit rules,
  transaction costs) rather than just marking the events

## License

MIT
