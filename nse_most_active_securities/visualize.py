"""
Generates three figures from output/most_active_analysis.csv, saved to
output/figures/:
1. Turnover share of each of the top 10 securities
2. Average trade size per security, with the market-wide average as a
   reference line
3. Number of trades vs traded quantity, marker size scaled to turnover
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from config import OUTPUT_DIR, MONTH_LABEL

FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"


def short_name(name: str) -> str:
    return name.replace(" Limited", "").replace(" Industries", " Ind.")


def load_data():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "most_active_analysis.csv"))
    totals = pd.read_csv(os.path.join(OUTPUT_DIR, "market_totals.csv"))
    return df, totals


def plot_turnover_share(df: pd.DataFrame):
    df = df.sort_values("Share in Total Turnover(%)")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(df["Security"].apply(short_name), df["Share in Total Turnover(%)"], color="tab:blue")
    ax.set_xlabel("Share of NSE-Wide Turnover (%)")
    ax.set_title(f"Turnover Share of the 10 Most Active Securities, {MONTH_LABEL}")
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "turnover_share.png"), dpi=150)
    plt.close(fig)


def plot_avg_trade_size(df: pd.DataFrame, totals: pd.DataFrame):
    market_total_row = totals[totals["Security"].str.upper() == "TOTAL"]
    market_avg_trade = (
        market_total_row["Turnover (₹ cr.)"].iloc[0] * 1e7
        / market_total_row["No. of Trades"].iloc[0]
    )

    df = df.sort_values("AvgTradeSizeRs")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(df["Security"].apply(short_name), df["AvgTradeSizeRs"], color="tab:orange")
    ax.axvline(market_avg_trade, color="black", linewidth=1.2, linestyle="--",
               label=f"NSE-wide average (Rs {market_avg_trade:,.0f})")
    ax.set_xlabel("Average Trade Size (Rs)")
    ax.set_title(f"Average Trade Size, {MONTH_LABEL}")
    ax.legend()
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "avg_trade_size.png"), dpi=150)
    plt.close(fig)


def plot_trades_vs_quantity(df: pd.DataFrame):
    # Numbered markers + a side legend, rather than inline text labels,
    # since several securities sit close together and inline labels
    # overlap in that cluster regardless of nudging.
    df = df.sort_values("Turnover (₹ cr.)", ascending=False).reset_index(drop=True)
    labels = [str(i + 1) for i in range(len(df))]
    sizes = df["Turnover (₹ cr.)"] / df["Turnover (₹ cr.)"].max() * 1800 + 200

    fig, ax = plt.subplots(figsize=(10, 6.5))
    x = df["No. of Trades"] / 1e5
    y = df["Traded Quantity (Lakh Shares)"]

    ax.scatter(x, y, s=sizes, alpha=0.55, color="tab:purple",
               edgecolors="black", linewidth=0.7, zorder=2)

    for xi, yi, label in zip(x, y, labels):
        ax.annotate(label, (xi, yi), ha="center", va="center",
                    fontsize=9, fontweight="bold", zorder=3)

    # Pad the axes so the largest bubbles (HDFC Bank, ETERNAL) don't
    # clip against the plot edge.
    ax.set_xlim(x.min() - 12, x.max() + 12)
    ax.set_ylim(y.min() - 700, y.max() + 700)

    legend_text = "\n".join(f"{i + 1}. {short_name(name)}" for i, name in enumerate(df["Security"]))
    ax.text(1.02, 0.98, legend_text, transform=ax.transAxes, fontsize=9,
            va="top", ha="left", linespacing=1.8)

    ax.set_xlabel("Number of Trades (Lakh)")
    ax.set_ylabel("Traded Quantity (Lakh Shares)")
    ax.set_title(f"Trade Count vs Traded Quantity, {MONTH_LABEL}\n(marker size = turnover)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "trades_vs_quantity.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    df, totals = load_data()
    plot_turnover_share(df)
    plot_avg_trade_size(df, totals)
    plot_trades_vs_quantity(df)
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
