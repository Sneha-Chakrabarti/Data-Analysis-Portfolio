"""
Generates three figures from the event study output, saved to
output/figures/:
1. Average cumulative abnormal return (CAR) across the event window,
   for all events, up-day events, and down-day events, on one plot
2. Distribution of events across the sample period, to show they are
   not all clustered in one market episode (e.g. only COVID)
3. Histogram of event-level 20-day CAR for up-day vs down-day events,
   showing the two distributions are genuinely separated, not just
   different in their means
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from config import OUTPUT_DIR

FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"


def plot_car_curve():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "car_by_day.csv"))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(df["RelativeDay"], df["AvgCAR_All"] * 100, color="black", linewidth=1.2,
            linestyle="--", label="All events (up + down pooled)")
    ax.plot(df["RelativeDay"], df["AvgCAR_Up"] * 100, color="tab:green", linewidth=1.6,
            label="Up-day volume shocks")
    ax.plot(df["RelativeDay"], df["AvgCAR_Down"] * 100, color="tab:red", linewidth=1.6,
            label="Down-day volume shocks")
    ax.axhline(0, color="grey", linewidth=0.7)
    ax.axvline(0, color="grey", linewidth=0.7, linestyle=":")

    ax.set_xlabel("Trading Days Relative to Volume-Shock Event (day 0)")
    ax.set_ylabel("Average Cumulative Abnormal Return (%)")
    ax.set_title("Volume-Shock Event Study: Average CAR Around the Event\n(458 events, 20 NSE stocks, 2011-2026)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "car_curve.png"), dpi=150)
    plt.close(fig)


def plot_event_distribution():
    events = pd.read_csv(os.path.join(OUTPUT_DIR, "events.csv"), parse_dates=["Date"])
    events["Year"] = events["Date"].dt.year
    counts = events.groupby(["Year", "Direction"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(counts.index, counts.get("Up", 0), label="Up-day", color="tab:green", alpha=0.8)
    ax.bar(counts.index, counts.get("Down", 0), bottom=counts.get("Up", 0),
           label="Down-day", color="tab:red", alpha=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Volume-Shock Events")
    ax.set_title("Volume-Shock Events by Year, Across 20 Stocks")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "events_by_year.png"), dpi=150)
    plt.close(fig)


def plot_car_histogram():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "event_level_car.csv"))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.hist(df[df.Direction == "Up"]["CAR_plus20"] * 100, bins=30, alpha=0.6,
            color="tab:green", label="Up-day events")
    ax.hist(df[df.Direction == "Down"]["CAR_plus20"] * 100, bins=30, alpha=0.6,
            color="tab:red", label="Down-day events")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("20-Day Cumulative Abnormal Return (%)")
    ax.set_ylabel("Number of Events")
    ax.set_title("Distribution of Individual Event 20-Day CAR")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "car_distribution.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    plot_car_curve()
    plot_event_distribution()
    plot_car_histogram()
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
