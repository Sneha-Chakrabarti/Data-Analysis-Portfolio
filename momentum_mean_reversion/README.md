# Event Study: Abnormal Volume Shocks and Subsequent Returns

An event study on the same 20-stock NSE universe used elsewhere in
this portfolio: identifies days where a stock's traded volume spikes
abnormally (a "volume shock"), then tests whether the market's
reaction to that shock predicts abnormal returns over the following
month. Includes a methodology correction made partway through this
project, kept visible rather than silently fixed, because it changes
the conclusion entirely.

## What this project shows

- A self-contained event study needing no external calendar or
  corporate-action data: events are defined purely from volume data
  already in this portfolio, avoiding the risk of misdating an
  external event
- Proper event-study mechanics: a market-adjusted abnormal return
  model, cumulative abnormal returns (CAR) over a defined event
  window, and a t-test for statistical significance across many
  events rather than eyeballing one or two examples
- A caught methodology error, shown rather than hidden: the first
  version of this analysis included the event day's own return in the
  "predictive" window, which is circular (the event's direction was
  defined by that same return), and produced a spuriously significant
  result. The corrected version excludes it, and the significant
  result disappears

## Data source

Same 20-stock NSE universe and source as `portfolio_construction_risk`
and `momentum_mean_reversion`: daily OHLCV (including volume) from
https://github.com/BennyThadikaran/eod2_data, 2011-01-01 to
2026-09-18. Raw CSVs copied into `data/raw/` for this project's
self-containment.

## Repository structure

```
volume_shock_event_study/
  config.py              universe, event thresholds, event window
  01_load_data.py           merges close prices and volume into two wide matrices
  02_identify_events.py       flags volume-shock events per stock
  03_event_study.py            computes AR/CAR and runs significance tests
  visualize.py                   generates the figures below
  requirements.txt
  data/raw/               20 raw per-stock CSVs
  data/prices_wide.csv     merged close-price matrix
  data/volume_wide.csv      merged volume matrix
  output/                  events, AR/CAR series, event-level CAR, figures
```

## Setup

```bash
git clone <your-repo-url>
cd volume_shock_event_study
pip install -r requirements.txt
```

## Usage

```bash
python 01_load_data.py         # data/prices_wide.csv, data/volume_wide.csv
python 02_identify_events.py   # output/events.csv
python 03_event_study.py       # output/car_by_day.csv, event_level_car.csv
python visualize.py            # output/figures/*.png
```

## Methodology

**Event definition**: a day is flagged as a volume-shock event for a
stock if that day's volume exceeds 5 times the trailing 60-day median
volume of that stock (median rather than mean, since daily volume is
right-skewed). The 60-day baseline uses only days strictly before the
event day. To avoid a single real spike being counted as several
separate events on consecutive high-volume days, a minimum gap of 10
trading days is enforced between two events for the same stock.

**Abnormal return model**: a simple market-adjusted return,
`AR = stock_return - market_return`, where the market proxy is the
equal-weight daily return across all 20 stocks in the universe.

**Event window**: 5 trading days before the event to 20 trading days
after (day 0 = the event day itself).

**Direction split**: each event is labeled Up or Down by its own
same-day return, splitting the sample into "volume shock on a rally"
versus "volume shock on a selloff," since these plausibly behave very
differently (a breakout versus a capitulation, in trading terminology).

## The methodology correction

The first version of this analysis measured post-event CAR from day 0
itself through day +5 and day +20. Because a shock's Up/Down label is
defined by day 0's own return, that specification necessarily starts
by re-adding roughly the same return that defined the label in the
first place, before any real "prediction" period has even begun. That
version showed:

| | CAR (+5 days) | CAR (+20 days) |
|---|---|---|
| Up-day events | +4.15% (t=11.50, p<0.0001) | +4.19% (t=8.65, p<0.0001) |
| Down-day events | -3.91% (t=-11.23, p<0.0001) | -3.66% (t=-6.60, p<0.0001) |

Both wildly significant, and wrong to interpret as predictive: they
mostly just confirm that a day labeled "up" had a positive return, and
a day labeled "down" had a negative one.

**The corrected version** measures CAR strictly from day +1 onward,
excluding the event day's own return entirely:

| | CAR (+5 days) | CAR (+20 days) |
|---|---|---|
| Up-day events | -0.42% (t=-1.55, p=0.122) | -0.37% (t=-0.90, p=0.367) |
| Down-day events | +0.07% (t=0.27, p=0.788) | +0.32% (t=0.63, p=0.527) |
| All events pooled | -0.19% (t=-1.03, p=0.302) | -0.05% (t=-0.15, p=0.882) |

None of these are statistically significant.

## Results

- **458 volume-shock events** identified across the 20 stocks and 15.7
  years (242 up-day, 216 down-day), reasonably spread across the
  sample period rather than clustered in a single crisis episode (see
  `events_by_year.png`; 2017 had the most events at 42, 2020's COVID
  year had 30, unremarkable relative to other years).
- **Once measured correctly, there is no statistically significant
  abnormal drift in the 5 or 20 trading days following a volume-shock
  event**, in either direction. The `car_curve.png` figure shows this
  directly: both the up-day and down-day average CAR lines jump
  sharply at day 0 (expected, since that is the day that defines the
  event) and are then essentially flat afterward, not still rising or
  falling.
- **The individual-event CAR distributions for up-day and down-day
  events are almost fully overlapping** (`car_distribution.png`), not
  two separated populations, consistent with the non-significant
  t-tests.
- **Read as a finding about the market rather than about the method**:
  this is consistent with semi-strong-form market efficiency for these
  20 large, liquid NSE stocks. A large volume shock is fully absorbed
  into the price by the close of the event day itself; there is no
  detectable, exploitable continuation or reversal pattern left over
  the following month.

See `output/figures/`:
1. `car_curve.png`: average CAR across the event window for all/up/down
   events, showing the day-0 jump and the flat post-event behavior
2. `events_by_year.png`: event counts by year, showing they are not
   concentrated in one episode
3. `car_distribution.png`: histogram of individual-event 20-day CAR
   for up-day vs down-day events, showing the overlap directly

## Limitations

- **A null result is not the same as proof of no effect**: 458 events
  gives reasonable but not enormous statistical power, particularly
  once split by direction (roughly 220-240 events each); a smaller
  true effect than this design can detect would still look like this
- **The market-adjusted return model is simple** (return minus an
  equal-weight 20-stock proxy); a proper market-model regression
  (stock return regressed on market return over an estimation window,
  producing stock-specific alpha and beta) is more standard in the
  academic event-study literature and was not used here
- **The 5x-median, 10-day-gap event definition is a stated choice**,
  not tuned or validated against alternative thresholds; a different
  threshold could identify a different, possibly differently-behaved,
  set of events
- Same survivorship-bias caveat as the sibling projects: today's
  large-caps traced backward, not a point-in-time universe

## Possible extensions

- Re-run with a proper market-model (regression-based) abnormal return
  specification instead of the simple market-adjusted version used here
- Test sensitivity to the event threshold (e.g. 3x or 8x median volume
  instead of 5x) and the minimum gap between events
- Extend the universe beyond 20 stocks for more statistical power,
  particularly within the direction-split subsamples

## License

MIT
