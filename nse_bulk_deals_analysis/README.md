# NSE Bulk Deals Analysis: Market-Making vs Genuine Institutional Conviction

Analysis of NSE Bulk Deals data for 8-11 September 2026 (740 individual
trade legs, 121 stocks, 171 distinct clients), separating same-day
round-trip trading (the signature of quant and market-making desks
providing liquidity) from genuine one-sided directional positions (the
signature of an actual investment decision).

## Background

A "bulk deal" on NSE is any single trade in one stock, by one client,
worth more than Rs 5 crore or exceeding a volume threshold, reported
separately from the normal trade feed. The published data lists each
leg (a BUY row and/or a SELL row) with no direct link between them, so
whether a client's activity in a stock that day was a genuine directional
bet or a same-day round trip has to be inferred from the data, not read
off a label.

## What this project shows

- Turning an unlabeled trade log into a labeled one, by building a
  classification rule and checking it against the data rather than
  taking a client's presence in the list at face value
- Distinguishing market microstructure activity (quant/prop desks doing
  near-simultaneous buys and sells to provide liquidity) from genuine
  institutional conviction trades (funds and individuals taking one-sided
  positions)
- Reading a real corporate-ownership event (a large individual seller
  matched against a consortium of institutional buyers) directly out of
  transaction-level data

## Data source

NSE Bulk Deals archive:
https://www.nseindia.com/report-detail/display-bulk-and-block-deals. The
uploaded export (`data/Bulk-Deals-08-09-2026-to-15-09-2026.csv`) covers
8 to 11 September 2026 (no deals were reported for 12-15 Sep in this
export, consistent with a weekend plus a day with no qualifying deals).

## Repository structure

```
nse-bulk-deals-analysis/
  config.py            file paths, round-trip classification threshold
  clean_data.py         parses the raw export, fixes formatting
  analyze.py             classifies deals, aggregates by client
  visualize.py            generates the figures below
  requirements.txt
  data/                  raw NSE export, as downloaded
  output/                cleaned data, computed CSVs, figures
```

## Setup

```bash
git clone <your-repo-url>
cd nse-bulk-deals-analysis
pip install -r requirements.txt
```

## Usage

```bash
python clean_data.py    # writes output/bulk_deals_cleaned.csv
python analyze.py       # writes output/bulk_deals_analysis.csv, client_summary.csv, directional_net_flow.csv
python visualize.py     # writes output/figures/*.png
```

## Methodology

Deals are grouped by (Date, Symbol, Client Name). Within a group:

    match_ratio = min(BuyQty, SellQty) / max(BuyQty, SellQty)

A group is classified **Round Trip** if both a BUY and a SELL leg exist
and `match_ratio >= 0.90` (the client bought and sold within 10 percent
of the same quantity, same stock, same day). Everything else, including
purely one-sided groups, is classified **Directional**.

**Net directional value** is `BuyValue - SellValue`, summed only across
groups classified Directional, and only tells you the net conviction
position, not round-trip turnover.

This is a heuristic, not a definitive classification: it can only see
what is reported as a bulk deal, not a client's full order book, and a
large one-sided position (matched with a counterparty who is not
individually large enough to appear as a bulk deal on the other side)
looks identical in the data to a genuine directional bet either way.

## Results

- **740 trade legs** resolved into **435 client-stock-day groups**.
  **236 of 435 (54.3%)** are round trips, accounting for **Rs 16,369
  crore, 72.6 percent of the Rs 22,557 crore total bulk-deal value** in
  this 4-day window. Most of the reported value in this dataset is
  liquidity provision, not directional conviction.
- **The top 4 clients by total value are all proprietary/quant trading
  firms** (Junomoneta Finsol, Microcurves Trading, HRTI, QE Securities),
  each with a round-trip share of 60 to 100 percent, together accounting
  for roughly Rs 12,545 crore of activity across dozens of small and
  mid-cap stocks.
- **A clear ownership-change event is visible directly in the data**: on
  11 Sep 2026, Krishna Prasad Chigurupati sold roughly 1.72 crore shares
  of Granules India (worth about Rs 1,509 crore) in two blocks, matched
  by BNP Paribas Financial Markets and SmallCap World Fund Inc buying at
  the same Rs 872.50 to 892.84 price band, both classified Directional
  with no round-trip signature (the name matches Granules India's
  promoter/chairman, though this export alone does not confirm that
  role).
- **A second clean block trade**: Pradeep Singh Jauhar and Randeep Singh
  Jauhar each sold exactly 99,95,000 shares of Jamna Auto Industries at a
  fixed Rs 128.00, matched against 360 ONE Asset Management, 360 ONE
  Mutual Fund, DSP Mutual Fund, and the Abu Dhabi Investment Authority
  buying at the identical price, a pattern consistent with a negotiated
  stake sale to a consortium of institutional buyers rather than open
  market activity.
- **Even a mutual fund can round-trip**: SBI Mutual Fund's only bulk deal
  in this window (Westlife Foodworld) was classified Round Trip, buying
  and selling near-identical quantities at an identical price on the
  same day, more likely an internal switch between fund schemes than a
  market view.

See `output/figures/`:
1. `top_clients.png`: top 15 clients by value, color-coded by round-trip
   share (red = mostly liquidity provision, green = mostly directional)
2. `classification_split.png`: round trip vs directional, by count and
   by value
3. `net_directional_flow.png`: largest net directional buyers and
   sellers

## Limitations

- Bulk deals are only trades that individually clear the reporting
  threshold; this is not a complete picture of any client's or stock's
  total trading activity for the period
- The 0.90 match-ratio threshold is a modeling choice, not an NSE
  definition; a different threshold would reclassify some borderline
  groups, particularly ones with a 70-90 percent quantity match
- Only 4 trading days are covered here; client roles (which firms are
  consistently market-makers vs consistently directional) would be
  more reliable over a longer window
- Client identity in the export is a name string; the same institution
  trading under slightly different registered names would not be merged

## Possible extensions

- Extend the classification across multiple weeks to see which clients
  are consistently round-trippers versus consistently directional, more
  reliable than a 4-day snapshot
- Cross-reference large directional sells against BSE/NSE shareholding
  pattern filings to confirm promoter versus non-promoter status
- Combine with the Block Deals report (separate from Bulk Deals, used
  for even larger single trades) for a fuller picture of large
  institutional activity

## License

MIT
