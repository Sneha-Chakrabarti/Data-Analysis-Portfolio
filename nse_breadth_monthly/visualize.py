"""
Generates two figures from output/breadth_monthly_analysis.csv, saved to
output/figures/:
1. Monthly Advance/Decline ratio with a 3-month rolling average and a
   reference line at 1.0
2. Cumulative monthly Advance-Decline Line
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
    path = os.path.join(OUTPUT_DIR, "breadth_monthly_analysis.csv")
    return pd.read_csv(path, parse_dates=["Month"])


def plot_ad_ratio(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["Month"], df["AD_Ratio"], color="tab:blue", linewidth=1.2,
            marker="o", markersize=3, label="Monthly A/D Ratio")
    ax.plot(df["Month"], df["AD_Ratio_Rolling"], color="tab:orange",
            linewidth=1.8, label="3-Month Rolling Average")
    ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--",
               label="Neutral (1.0)")

    ax.set_xlabel("Month")
    ax.set_ylabel("Advance / Decline Ratio")
    ax.set_title("NSE Monthly Advance/Decline Ratio, 2021 to 2026")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "ad_ratio_monthly.png"), dpi=150)
    plt.close(fig)


def plot_ad_line(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["Month"], df["AD_Line_Monthly"], color="tab:purple", linewidth=1.6)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

    ax.set_xlabel("Month")
    ax.set_ylabel("Cumulative Net Advances")
    ax.set_title("NSE Monthly Advance-Decline Line, 2021 to 2026")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "ad_line_monthly.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    df = load_data()
    plot_ad_ratio(df)
    plot_ad_line(df)
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
