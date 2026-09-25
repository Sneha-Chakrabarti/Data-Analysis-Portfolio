"""
For each stock, flags a day as a volume-shock event if that day's
volume exceeds VOLUME_SHOCK_MULTIPLE times the trailing 60-day median
volume (using only the 60 days strictly before the event day, so the
event day's own volume never contaminates its own baseline). After
flagging candidates, enforces a minimum gap of MIN_GAP_BETWEEN_EVENTS
trading days between two events for the same stock, keeping only the
first day of a multi-day spike so a single real shock is not counted
several times.

Saves output/events.csv: one row per event, with the stock, date,
same-day return, and a same-day-up/down classification used to split
the event study later.
"""

import os
import pandas as pd

from config import (
    DATA_DIR, OUTPUT_DIR, UNIVERSE, VOLUME_LOOKBACK, VOLUME_SHOCK_MULTIPLE,
    MIN_GAP_BETWEEN_EVENTS, MIN_HISTORY,
)


def find_events_for_stock(prices: pd.Series, volume: pd.Series, symbol: str) -> list:
    returns = prices.pct_change()
    trailing_median = volume.rolling(VOLUME_LOOKBACK).median().shift(1)  # shift(1): strictly before today
    shock_ratio = volume / trailing_median

    candidates = shock_ratio[shock_ratio > VOLUME_SHOCK_MULTIPLE].index
    candidates = [d for d in candidates if volume.index.get_loc(d) >= MIN_HISTORY]

    events = []
    last_event_loc = -10**9
    for date in candidates:
        loc = volume.index.get_loc(date)
        if loc - last_event_loc < MIN_GAP_BETWEEN_EVENTS:
            continue
        last_event_loc = loc
        events.append({
            "Symbol": symbol,
            "Date": date,
            "VolumeShockRatio": shock_ratio.loc[date],
            "SameDayReturn": returns.loc[date],
            "Direction": "Up" if returns.loc[date] > 0 else "Down",
        })
    return events


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prices = pd.read_csv(os.path.join(DATA_DIR, "prices_wide.csv"), index_col="Date", parse_dates=True)
    volume = pd.read_csv(os.path.join(DATA_DIR, "volume_wide.csv"), index_col="Date", parse_dates=True)

    all_events = []
    for symbol in UNIVERSE:
        all_events.extend(find_events_for_stock(prices[symbol], volume[symbol], symbol))

    events_df = pd.DataFrame(all_events).sort_values(["Date", "Symbol"]).reset_index(drop=True)
    events_df.to_csv(os.path.join(OUTPUT_DIR, "events.csv"), index=False)

    print(f"Found {len(events_df)} volume-shock events across {len(UNIVERSE)} stocks")
    print(f"  Up-day events: {(events_df['Direction'] == 'Up').sum()}")
    print(f"  Down-day events: {(events_df['Direction'] == 'Down').sum()}")
    print("\nEvents per stock:")
    print(events_df["Symbol"].value_counts().to_string())
    print(f"\nSaved to {os.path.join(OUTPUT_DIR, 'events.csv')}")


if __name__ == "__main__":
    main()
