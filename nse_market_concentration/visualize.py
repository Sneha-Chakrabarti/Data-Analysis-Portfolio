"""
Generates three figures from output/concentration_analysis.csv, saved to
output/figures/:
1. Securities-side Top-N turnover share over time, all 5 N-values on one
   plot
2. Members-side Top-N turnover share over time, all 5 N-values on one
   plot
3. Top 10 securities vs Top 10 members share, on twin axes, to show the
   diverging trend directly
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from config import OUTPUT_DIR

FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"

SEC_COLS = ["Securities_Top5", "Securities_Top10", "Securities_Top25",
            "Securities_Top50", "Securities_Top100"]
MEM_COLS = ["Members_Top5", "Members_Top10", "Members_Top25",
            "Members_Top50", "Members_Top100"]
N_LABELS = ["Top 5", "Top 10", "Top 25", "Top 50", "Top 100"]


def load_data() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "concentration_analysis.csv"), parse_dates=["MonthDate"])
    return df


def plot_side(df: pd.DataFrame, cols, title, filename):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for col, label in zip(cols, N_LABELS):
        ax.plot(df["MonthDate"], df[col], linewidth=1.5, label=label)

    ax.set_xlabel("Month")
    ax.set_ylabel("Share of NSE Turnover (%)")
    ax.set_title(title)
    ax.legend(title="Group size", ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.15))
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, filename), dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_top10_comparison(df: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(11, 5.5))

    ax1.plot(df["MonthDate"], df["Securities_Top10"], color="tab:blue", linewidth=1.8,
             label="Top 10 Securities")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Top 10 Securities Share (%)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.plot(df["MonthDate"], df["Members_Top10"], color="tab:red", linewidth=1.8,
             label="Top 10 Members")
    ax2.set_ylabel("Top 10 Members Share (%)", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax1.set_title("Top 10 Securities Share (falling) vs Top 10 Members Share (rising)")
    ax1.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "top10_securities_vs_members.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    df = load_data()
    plot_side(df, SEC_COLS, "Securities-Side Concentration: Share of NSE Turnover by Top-N Stocks", "securities_concentration.png")
    plot_side(df, MEM_COLS, "Member-Side Concentration: Share of NSE Turnover by Top-N Brokers", "members_concentration.png")
    plot_top10_comparison(df)
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
