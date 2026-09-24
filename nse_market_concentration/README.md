# NSE Market Concentration: Securities vs Members, 2022 to 2026

Analysis of NSE's "Percentage Share of Top 'N' Securities/Members"
report, monthly from April 2022 to August 2026 (53 months): how much of
total NSE turnover is concentrated in the most-traded stocks, and
separately, how much is concentrated among the most active broker
members, and how those two concentration patterns have moved in opposite
directions over more than four years.

## What this project shows

- Turning a wide, repeating monthly report (5 years of screenshots, 2
  tables each) into one clean long-format time series
- A genuinely counter-intuitive finding stated plainly: turnover has
  become less concentrated among top stocks over time, while it has
  become slightly more concentrated among top brokers, the opposite
  directions, in the same market, over the same period
- Using NSE's own reporting-year convention (April to March) rather than
  the calendar year, since that is how the underlying data is structured

## Data source

NSE's Percentage Share of Top 'N' Securities/Members archive:
https://www.nseindia.com/historical/top-n-securities-members. Transcribed
by hand from the NSE site for April 2022 through August 2026, stored in
`data/top_n_share_monthly.csv`. Each row gives, for that month, the
percentage of total NSE turnover accounted for by the top 5, 10, 25, 50,
and 100 securities (by turnover), and separately by the top 5, 10, 25,
50, and 100 members (broker/trading members, by turnover).

## Repository structure

```
nse-market-concentration/
  config.py            file paths, rolling window size
  analyze.py             rolling averages, fiscal-year summary, trends
  visualize.py            generates the figures below
  requirements.txt
  data/top_n_share_monthly.csv   the source data (53 months)
  output/                computed CSVs and figures
```

## Setup

```bash
git clone <your-repo-url>
cd nse-market-concentration
pip install -r requirements.txt
```

## Usage

```bash
python analyze.py       # writes output/concentration_analysis.csv, fiscal_year_summary.csv
python visualize.py     # writes output/figures/*.png
```

## Methodology

Fiscal year is assigned NSE-style (April to March): a row dated 2022-04
through 2023-03 belongs to fiscal year "2022-2023". Trend is a simple
linear fit (least squares) of each Top-N series against month index,
reported in percentage points per month and per year. A 3-month rolling
average is also computed for each series to smooth month-to-month noise.

## Results

**Securities-side concentration has fallen steadily.** Comparing the
first month (Apr 2022) to the latest (Aug 2026):

| Group | Apr 2022 | Aug 2026 | Change |
|-------|----------|----------|--------|
| Top 5 securities | 14% | 7% | -7 pp |
| Top 10 securities | 22% | 11% | -11 pp |
| Top 25 securities | 36% | 21% | -15 pp |
| Top 50 securities | 50% | 31% | -19 pp |
| Top 100 securities | 65% | 45% | -20 pp |

The linear trend confirms this isn't just endpoint noise: Top 10
securities share fell at -1.61 percentage points per year and Top 100
fell at -2.92 points per year, both fitted over the full 53-month
series. Turnover has broadened across more stocks over time rather than
staying concentrated in the same handful of large names.

**Member (broker) concentration moved the opposite way, slightly.**

| Group | Apr 2022 | Aug 2026 | Change |
|-------|----------|----------|--------|
| Top 5 members | 26% | 27% | +1 pp |
| Top 10 members | 39% | 42% | +3 pp |
| Top 25 members | 60% | 64% | +4 pp |
| Top 50 members | 77% | 79% | +2 pp |
| Top 100 members | 89% | 91% | +2 pp |

Small moves, but consistently upward (Top 10 members: +1.45 points per
year), and starting from a much higher base: the top 100 brokers have
handled 88 to 92 percent of all NSE turnover throughout the entire
period, versus 45 to 67 percent for the top 100 stocks. Trading is, and
has remained, far more concentrated by broker than by stock.

**A sharp temporary spike in securities concentration around early
2023**: Top 5 securities share jumped from 9% (Dec 2022) to 19% (Apr
2023), and Top 100 from 58% to 67%, before falling back over the rest of
2023. This window overlaps with a period of major volatility in a few
large Indian conglomerate stocks; this dataset shows the concentration
spike clearly but does not itself identify the cause.

See `output/figures/`:
1. `securities_concentration.png`: all 5 securities Top-N series over
   time
2. `members_concentration.png`: all 5 members Top-N series over time
3. `top10_securities_vs_members.png`: Top 10 securities and Top 10
   members plotted together (twin axes) to show the diverging trend
   directly

## Limitations

- Data was transcribed by hand from screenshots rather than fetched
  programmatically; spot-check a few months against the live NSE page
  before relying on this for anything beyond a portfolio piece
- The report itself does not explain why concentration moves the way it
  does; the early-2023 spike is flagged but not investigated here
- "Members" are broker/trading members, not individual traders; a small
  number of large brokerage firms serving many retail clients would
  still show up as high member concentration even with broad retail
  participation

## Possible extensions

- Overlay Nifty50 volatility (e.g. India VIX) over the same period to
  test whether securities concentration spikes coincide with volatility
  spikes
- Extend backward before April 2022 if older archive data is available
- Break down which specific securities/members are driving the Top 5
  and Top 10 figures, this report only gives the aggregate share, not
  the constituent names

## License

MIT
