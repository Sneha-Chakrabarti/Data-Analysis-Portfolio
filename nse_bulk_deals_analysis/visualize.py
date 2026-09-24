"""
Generates three figures from the analysis output, saved to
output/figures/:
1. Top 15 clients by total bulk-deal value, colored by round-trip share
2. Round trip vs directional deal count and value
3. Top net directional buyers and sellers (diverging bar chart)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from config import OUTPUT_DIR

FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"


def plot_top_clients():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "client_summary.csv"))
    top = df.head(15).sort_values("TotalValue")

    colors = plt.cm.RdYlGn_r(top["RoundTripShare"])

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(top["Client Name"], top["TotalValue"] / 1e7, color=colors)
    ax.set_xlabel("Total Traded Value (Rs Crore)")
    ax.set_title("Top 15 Clients by Bulk-Deal Value\n(red = mostly round trips, green = mostly directional)")
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "top_clients.png"), dpi=150)
    plt.close(fig)


def plot_classification_split():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "bulk_deals_analysis.csv"))
    counts = df["Classification"].value_counts()
    values = df.groupby("Classification")["TotalValue"].sum() / 1e7

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    axes[0].bar(counts.index, counts.values, color=["tab:red", "tab:green"])
    axes[0].set_ylabel("Number of Client-Stock-Day Groups")
    axes[0].set_title("Deal Count")
    axes[0].grid(alpha=0.3, axis="y")

    axes[1].bar(values.index, values.values, color=["tab:red", "tab:green"])
    axes[1].set_ylabel("Total Value (Rs Crore)")
    axes[1].set_title("Deal Value")
    axes[1].grid(alpha=0.3, axis="y")

    fig.suptitle("Round Trip (Market-Making) vs Directional Bulk Deals, 8-11 Sep 2026")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "classification_split.png"), dpi=150)
    plt.close(fig)


def plot_net_flow():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "directional_net_flow.csv"))
    top_buyers = df.head(8)
    top_sellers = df.tail(8)
    combined = pd.concat([top_sellers, top_buyers]).sort_values("NetValue")

    colors = ["tab:red" if v < 0 else "tab:green" for v in combined["NetValue"]]

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(combined["Client Name"], combined["NetValue"] / 1e7, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Net Directional Value (Rs Crore, positive = net buyer)")
    ax.set_title("Largest Net Directional Buyers and Sellers")
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "net_directional_flow.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    plot_top_clients()
    plot_classification_split()
    plot_net_flow()
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
