# NSE Most Active Securities: Turnover Concentration, August 2026

Analysis of NSE's Most Active Securities report for August 2026: the top
10 stocks by turnover, and how their trading behavior compares to the
NSE-wide average for the month.

## What this project shows

- Working with a genuinely small, summary-level dataset (10 rows plus 2
  totals) rather than assuming more granular data is always needed for a
  real finding
- Deriving a sanity-check metric (implied average traded price = turnover
  divided by volume) to catch data errors before drawing conclusions from
  a report, not just to fill a column
- A concentration finding stated with the right qualifier: 10 stocks
  moved almost 11 percent of all NSE turnover on just 4.9 percent of all
  trades, meaning each of those trades was on average far larger than a
  typical NSE trade that month

## Data source

NSE's Most Active Securities archive:
https://www.nseindia.com/historical/most-active-securities. The uploaded
export (`data/Most_Active_Securities_-_August_2026.csv`) is the August
2026 monthly report, top 10 securities by turnover plus NSE-wide totals.

## Repository structure

```
nse-most-active-securities/
  config.py            file paths, month label
  clean_data.py         parses the raw export, splits securities from totals
  analyze.py             average trade size, implied price, concentration
  visualize.py            generates the figures below
  requirements.txt
  data/                  raw NSE export, as downloaded
  output/                cleaned data, computed CSVs, figures
```

## Setup

```bash
git clone <your-repo-url>
cd nse-most-active-securities
pip install -r requirements.txt
```

## Usage

```bash
python clean_data.py    # writes output/most_active_cleaned.csv, output/market_totals.csv
python analyze.py       # writes output/most_active_analysis.csv, prints summary
python visualize.py     # writes output/figures/*.png
```

## Methodology

    AvgTradeSizeRs    = (Turnover in Rs crore * 1e7) / No. of Trades
    ImpliedAvgPriceRs = (Turnover in Rs crore * 1e7) / (Traded Quantity in lakh shares * 1e5)

`ImpliedAvgPriceRs` is not a data column NSE publishes; it is turnover
divided by volume, which should land close to the stock's actual average
traded price for the month. It is included as an internal consistency
check on the report's own numbers (a wildly implausible implied price
would flag a parsing error or a units mismatch) rather than as a
verified market price.

## Results

- **Top 10 securities' turnover**: Rs 274,395 crore, **10.92% of NSE's
  total Rs 2,513,308 crore turnover** for the month
- **Top 10 securities' trade count**: 3.72 crore trades, only **4.90% of
  the 75.90 crore total trades** on NSE that month
- **Average trade size**: Rs 33,114 NSE-wide, versus **Rs 73,764 within
  the top 10**, more than double. The stocks that dominate turnover get
  there disproportionately through larger trades, not simply a higher
  trade count, consistent with heavier institutional or algorithmic
  participation in the most liquid names
- **Every one of the top 10 individually has an average trade size above
  the NSE-wide average**, not just the group as a whole (see
  `avg_trade_size.png`); ICICI Bank and Bharti Airtel have the largest
  average trade sizes in the group (Rs 95,691 and Rs 94,574), Hindustan
  Copper the smallest (Rs 50,808), still 53% above the market-wide figure
- **Turnover share is fairly flat across the top 10**: from HDFC Bank at
  1.69% down to Hindustan Copper at 0.80%, no single name dominates the
  group the way "most active" lists sometimes suggest

See `output/figures/`:
1. `turnover_share.png`: each security's share of NSE-wide turnover
2. `avg_trade_size.png`: average trade size per security against the
   NSE-wide reference line
3. `trades_vs_quantity.png`: trade count vs traded quantity, marker size
   scaled to turnover, useful for spotting names that are active on
   volume versus active on value

## Limitations

- Single month, top 10 only; this cannot say whether these names are
  consistently the most active or just had an unusual August
- Turnover-based ranking mechanically favors higher-priced and
  higher-value stocks over high-volume, low-price stocks; a
  volume-ranked version of this report would likely list a different set
  of names
- No breakdown of trade size distribution within a stock, the average
  trade size figure could hide a mix of many small retail trades and a
  few very large block trades rather than reflecting a uniformly large
  typical trade

## Possible extensions

- Pull several months of this report and track which names stay in the
  top 10 versus rotate in and out
- Cross-reference against the Bulk Deals data (see `nse-bulk-deals-analysis`
  in this same project series) to check whether high average trade size
  in a name coincides with bulk-deal activity that month
- Add a volume-ranked version alongside the turnover-ranked one

## License

MIT
