"""
For every event in output/events.csv, extracts the stock's daily
return in a window from PRE_WINDOW days before to POST_WINDOW days
after the event day (day 0), computes the market-adjusted abnormal
return each day (AR = stock return - equal-weight 20-stock market
return, a simple market-adjusted-return model), and cumulates it into
CAR (cumulative abnormal return) within the event window.

Averages AR and CAR across all events at each relative day, and
separately for the Up-day and Down-day subsets, to see whether the
market's reaction to a volume shock differs by the same-day direction
of that shock.

A t-test is run on the average CAR at two horizons (+5 and +20 days
after the event) to check whether the post-event drift, if any, is
distinguishable from zero given the number of events.

Saves output/car_by_day.csv (average AR/CAR at every relative day, for
All/Up/Down) and output/event_level_car.csv (each individual event's
CAR at +5 and +20, for the significance test).
"""

import os
import numpy as np
import pandas as pd
from scipy import stats

from config import DATA_DIR, OUTPUT_DIR, UNIVERSE, PRE_WINDOW, POST_WINDOW


def main():
    prices = pd.read_csv(os.path.join(DATA_DIR, "prices_wide.csv"), index_col="Date", parse_dates=True)
    returns = prices.pct_change()
    market_return = returns[UNIVERSE].mean(axis=1)  # simple equal-weight 20-stock proxy

    events = pd.read_csv(os.path.join(OUTPUT_DIR, "events.csv"), parse_dates=["Date"])

    relative_days = list(range(-PRE_WINDOW, POST_WINDOW + 1))
    event_car_records = []
    ar_matrix = {rd: [] for rd in relative_days}  # relative_day -> list of AR across events
    direction_ar_matrix = {
        "Up": {rd: [] for rd in relative_days},
        "Down": {rd: [] for rd in relative_days},
    }

    skipped = 0
    for _, ev in events.iterrows():
        symbol, event_date, direction = ev["Symbol"], ev["Date"], ev["Direction"]
        if event_date not in returns.index:
            skipped += 1
            continue
        loc = returns.index.get_loc(event_date)
        if loc - PRE_WINDOW < 0 or loc + POST_WINDOW >= len(returns):
            skipped += 1
            continue  # too close to the start/end of the sample for a full window

        stock_ret = returns[symbol].iloc[loc - PRE_WINDOW: loc + POST_WINDOW + 1].values
        mkt_ret = market_return.iloc[loc - PRE_WINDOW: loc + POST_WINDOW + 1].values
        ar = stock_ret - mkt_ret

        cum_ar = np.cumsum(ar)
        for j, rd in enumerate(relative_days):
            ar_matrix[rd].append(ar[j])
            direction_ar_matrix[direction][rd].append(ar[j])

        # +5 and +20 day CAR measured strictly AFTER the event day,
        # from day +1 through day +5 / +20. Day 0 itself is excluded
        # on purpose: Direction was defined by day 0's own return, so
        # including day 0 in the CAR would trivially reproduce that
        # same return rather than testing whether the shock actually
        # predicts anything about what happens afterward.
        zero_idx = relative_days.index(0)
        car_plus5 = cum_ar[zero_idx + 5] - cum_ar[zero_idx]
        car_plus20 = cum_ar[zero_idx + 20] - cum_ar[zero_idx]
        event_car_records.append({
            "Symbol": symbol, "Date": event_date, "Direction": direction,
            "CAR_plus5": car_plus5, "CAR_plus20": car_plus20,
        })

    event_car_df = pd.DataFrame(event_car_records)
    event_car_df.to_csv(os.path.join(OUTPUT_DIR, "event_level_car.csv"), index=False)

    rows = []
    for rd in relative_days:
        row = {
            "RelativeDay": rd,
            "AvgAR_All": np.mean(ar_matrix[rd]),
            "AvgAR_Up": np.mean(direction_ar_matrix["Up"][rd]),
            "AvgAR_Down": np.mean(direction_ar_matrix["Down"][rd]),
        }
        rows.append(row)
    car_by_day = pd.DataFrame(rows)
    car_by_day["AvgCAR_All"] = car_by_day["AvgAR_All"].cumsum()
    car_by_day["AvgCAR_Up"] = car_by_day["AvgAR_Up"].cumsum()
    car_by_day["AvgCAR_Down"] = car_by_day["AvgAR_Down"].cumsum()
    car_by_day.to_csv(os.path.join(OUTPUT_DIR, "car_by_day.csv"), index=False)

    print(f"{len(event_car_df)} events used ({skipped} skipped: too close to sample edge)\n")

    for label, subset in [("All", event_car_df),
                           ("Up-day", event_car_df[event_car_df.Direction == "Up"]),
                           ("Down-day", event_car_df[event_car_df.Direction == "Down"])]:
        for horizon in ["CAR_plus5", "CAR_plus20"]:
            vals = subset[horizon].dropna()
            t_stat, p_val = stats.ttest_1samp(vals, 0)
            print(f"{label} {horizon}: mean={vals.mean():+.4%}, n={len(vals)}, "
                  f"t={t_stat:.2f}, p={p_val:.4f}")
        print()


if __name__ == "__main__":
    main()
