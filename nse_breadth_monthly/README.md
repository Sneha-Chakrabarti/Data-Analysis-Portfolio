# NSE Monthly Market Breadth Analysis (2021 to 2026)

Analysis of NSE-wide monthly advances and declines from January 2021 to
August 2026 (68 months), tracking whether market gains have been broad
(most stocks participating) or narrow (a shrinking set of stocks driving
the index), and whether that has shifted over the period.

## What this project shows

- Working with a small, manually-sourced real dataset rather than a
  packaged Kaggle CSV
- Building derived indicators (ratio, cumulative line, rolling average)
  from two raw counts
- Reading a multi-year trend and stating a clear, specific finding
- Catching and flagging a data quality issue in the source rather than
  taking it at face value

## Data source

NSE's monthly Advances/Declines report
(https://www.nseindia.com/historical/advances-declines), showing the
count of NSE-listed stocks that closed higher (advances) versus lower
(declines) each month. Transcribed by hand from the NSE archive pages for
January 2021 through August 2026, stored in
`data/advances_declines_monthly.csv`.

**Data quality note.** NSE's own "Advance/Decline Ratio" column does not
always match Advances divided by Declines for that row (for example,
April 2022 is listed as 1,081 advances, 1,069 declines, ratio 1.41, but
1081/1069 is 1.01). This analysis recomputes the ratio directly from the
Advances and Declines counts rather than trusting the published ratio
column, and that recomputed ratio is what all the figures and stats below
use.

## Repository structure

```
nse-breadth-monthly/
  config.py                        file paths, rolling window size
  analyze_breadth.py                computes ratio, net advances, AD line
  visualize.py                      generates the figures below
  requirements.txt
  data/advances_declines_monthly.csv   the source data (68 months)
  output/                           computed CSV and figures
```

## Setup

```bash
git clone <your-repo-url>
cd nse-breadth-monthly
pip install -r requirements.txt
```

## Usage

```bash
python analyze_breadth.py    # writes output/breadth_monthly_analysis.csv
python visualize.py          # writes output/figures/*.png
```

## Methodology

    AD_Ratio        = Advances / Declines
    NetAdvances      = Advances - Declines
    AD_Line_Monthly  = cumulative sum of NetAdvances across all months
    AD_Ratio_Rolling = 3-month rolling average of AD_Ratio

A month is classified breadth-positive if its AD ratio exceeds 1.0 (more
advancing stocks than declining stocks that month).

## Results

- **24 of 68 months (35 percent)** were breadth-positive (AD ratio above
  1.0). Declines outnumbered advances in nearly two-thirds of all months
  in this period.
- **Year-by-year average AD ratio**: 2021 0.99, 2022 0.94, 2023 0.99, 2024
  0.94, 2025 0.93, 2026 (through August) 1.02. Every full year from 2021
  to 2025 averaged below 1.0; 2026 is the first year in the dataset to
  average above it.
- **The cumulative Advance-Decline Line has been net negative for almost
  the entire period.** It turned negative in early 2021 and did not
  recover, reaching its low point of -5,175 in March 2026 before a partial
  recovery to -4,326 by August 2026.
- **Widest single-month swings**: April 2026 was the strongest
  breadth month in the dataset (2,146 advances vs 1,373 declines, ratio
  1.56), immediately preceded by March 2026, one of the weakest (1,482
  advances vs 2,020 declines, ratio 0.73). A sharp one-month reversal.
- **Weakest month overall**: February 2025 (1,066 advances vs 1,755
  declines, ratio 0.61).

See `output/figures/`:
1. `ad_ratio_monthly.png`: monthly ratio with 3-month rolling average and
   a neutral reference line at 1.0
2. `ad_line_monthly.png`: cumulative net advances, showing the multi-year
   negative drift and 2026 partial recovery

## Interpretation

Because this is monthly-aggregated data rather than daily, it cannot say
anything about intraday or week-to-week breadth dynamics, only the
broader multi-year pattern: NSE market breadth was structurally negative
for most of 2021 to 2025 even as the Nifty50 index itself trended higher
over parts of that window (a classic sign that gains were concentrated in
large-cap and index-heavyweight stocks rather than broad-based). Whether
this is actually true would need the Nifty50 index series lined up
against this data, which is the natural next step.

## Possible extensions

- Overlay Nifty50 monthly closing levels against the AD Line to check
  whether breadth diverged from the index (the daily version of this
  analysis, `nse-market-breadth`, does this at daily resolution)
- Extend the series further back for a longer-run comparison
- Break the monthly counts down by sector or index constituent group, if
  that granularity becomes available
- Automate the monthly transcription with a scraper against NSE's
  archive page, since this dataset was compiled by hand

## License

MIT
