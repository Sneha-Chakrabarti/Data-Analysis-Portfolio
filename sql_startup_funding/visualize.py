"""
Generates four figures from the analysis output CSVs, saved to
output/figures/:
1. Yearly deal count and disclosure rate
2. Top 10 industries by disclosed funding
3. Top 10 cities by disclosed funding
4. Monthly deal count trend
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from config import OUTPUT_DIR

FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"


def plot_yearly():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "02_analysis_yearly.csv"))
    df["year"] = df["year"].astype(str)
    df = df[df["year"] != "2020"].copy()  # only 7 rows in this export, not a full year

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.bar(df["year"].astype(str), df["deal_count"], color="tab:blue", alpha=0.7, label="Deal count")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Deal Count", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.plot(df["year"].astype(str), df["disclosure_rate_pct"], color="tab:red",
             linewidth=2, marker="o", label="Disclosure rate")
    ax2.set_ylabel("Amount-Disclosure Rate (%)", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")
    ax2.set_ylim(0, 100)

    ax1.set_title("Indian Startup Funding: Deal Count and Disclosure Rate by Year\n(2015-2019; 2020 excluded, only 7 days of data in this export)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "yearly_deals_disclosure.png"), dpi=150)
    plt.close(fig)


def plot_top_industries():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "03_analysis_industries.csv")).head(10)
    df = df.sort_values("total_disclosed_usd")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(df["industry_vertical"], df["total_disclosed_usd"] / 1e9, color="tab:green")
    ax.set_xlabel("Total Disclosed Funding (USD Billion)")
    ax.set_title("Top 10 Industry Verticals by Disclosed Funding, 2015-2020")
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "top_industries.png"), dpi=150)
    plt.close(fig)


def plot_top_cities():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "04_analysis_cities.csv")).head(10)
    df = df.sort_values("total_disclosed_usd")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(df["city"], df["total_disclosed_usd"] / 1e9, color="tab:orange")
    ax.set_xlabel("Total Disclosed Funding (USD Billion)")
    ax.set_title("Top 10 Cities by Disclosed Funding, 2015-2020 (after standardizing city names)")
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "top_cities.png"), dpi=150)
    plt.close(fig)


def plot_monthly_trend():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "08_analysis_monthly_trend.csv"))

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["year_month"], df["deal_count"], color="tab:purple", linewidth=1.3)
    ax.set_xlabel("Month")
    ax.set_ylabel("Deal Count")
    ax.set_title("Monthly Deal Count, 2015-2020")
    ax.grid(alpha=0.3)

    tick_positions = range(0, len(df), 6)
    ax.set_xticks([df["year_month"].iloc[i] for i in tick_positions])
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "monthly_trend.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    plot_yearly()
    plot_top_industries()
    plot_top_cities()
    plot_monthly_trend()
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
