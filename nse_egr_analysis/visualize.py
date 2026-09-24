"""
Generates three figures from output/egr_analysis.csv, saved to
output/figures/:
1. Close price trend over the period
2. Daily returns (bar chart)
3. Traded quantity vs traded value (twin y-axis, single plot)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from config import OUTPUT_DIR

FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"


def load_data() -> pd.DataFrame:
    path = os.path.join(OUTPUT_DIR, "egr_analysis.csv")
    return pd.read_csv(path, parse_dates=["Date"])


def plot_price_trend(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df["Date"], df["Close Price"], color="tab:orange", linewidth=1.6,
            marker="o", markersize=4)
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price (Rs per 10g)")
    ax.set_title("GOLD10G99 (EGR) Close Price, 17-Aug-2026 to 11-Sep-2026")
    ax.grid(alpha=0.3)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "price_trend.png"), dpi=150)
    plt.close(fig)


def plot_daily_returns(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = ["tab:green" if r >= 0 else "tab:red" for r in df["DailyReturn"].fillna(0)]
    ax.bar(df["Date"], df["DailyReturn"] * 100, color=colors, width=0.6)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Return (%)")
    ax.set_title("GOLD10G99 (EGR) Daily Returns")
    ax.grid(alpha=0.3, axis="y")
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "daily_returns.png"), dpi=150)
    plt.close(fig)


def plot_liquidity(df: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(9, 5))

    ax1.bar(df["Date"], df["Total Traded Quantity"], color="tab:blue", alpha=0.6,
            width=0.6, label="Traded Quantity")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Traded Quantity (units)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.plot(df["Date"], df["Value"], color="tab:red", linewidth=1.8,
             marker="o", markersize=3, label="Traded Value")
    ax2.set_ylabel("Traded Value (Rs)", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    ax1.set_title("GOLD10G99 (EGR) Daily Liquidity")
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "liquidity.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    df = load_data()
    plot_price_trend(df)
    plot_daily_returns(df)
    plot_liquidity(df)
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
