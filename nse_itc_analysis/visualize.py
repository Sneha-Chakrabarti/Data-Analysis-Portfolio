"""
Generates four figures from output/itc_analysis.csv, saved to
output/figures/:
1. Close price with 50-day and 200-day moving averages, golden/death
   cross points marked
2. Drawdown from running peak
3. Delivery percentage trend with its own rolling average
4. Daily traded volume
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from config import OUTPUT_DIR, SMA_SHORT, SMA_LONG

FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"


def load_data() -> pd.DataFrame:
    path = os.path.join(OUTPUT_DIR, "itc_analysis.csv")
    return pd.read_csv(path, parse_dates=["Date"])


def plot_price_with_moving_averages(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(df["Date"], df["Close Price"], color="tab:blue", linewidth=1.0,
            alpha=0.7, label="Close Price")
    ax.plot(df["Date"], df[f"SMA{SMA_SHORT}"], color="tab:orange", linewidth=1.5,
            label=f"{SMA_SHORT}-Day SMA")
    ax.plot(df["Date"], df[f"SMA{SMA_LONG}"], color="tab:red", linewidth=1.5,
            label=f"{SMA_LONG}-Day SMA")

    golden = df[df["GoldenCross"]]
    death = df[df["DeathCross"]]
    ax.scatter(golden["Date"], golden["Close Price"], color="green", marker="^",
               s=70, label="Golden Cross", zorder=5)
    ax.scatter(death["Date"], death["Close Price"], color="black", marker="v",
               s=70, label="Death Cross", zorder=5)

    ax.set_xlabel("Date")
    ax.set_ylabel("Price (Rs)")
    ax.set_title("ITC: Close Price with 50/200-Day Moving Averages, 2021 to 2026")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "price_with_moving_averages.png"), dpi=150)
    plt.close(fig)


def plot_drawdown(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(df["Date"], df["Drawdown"] * 100, color="tab:red", linewidth=1.2)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown from Peak (%)")
    ax.set_title("ITC: Drawdown from Running Peak")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "drawdown.png"), dpi=150)
    plt.close(fig)


def plot_delivery_pct(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    rolling = df["% Dly Qt to Traded Qty"].rolling(20).mean()
    ax.plot(df["Date"], df["% Dly Qt to Traded Qty"], color="tab:blue",
            linewidth=0.6, alpha=0.4, label="Daily Delivery %")
    ax.plot(df["Date"], rolling, color="tab:blue", linewidth=1.8,
            label="20-Day Rolling Average")
    ax.set_xlabel("Date")
    ax.set_ylabel("Delivery Percentage (%)")
    ax.set_title("ITC: Percentage of Traded Quantity Delivered")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "delivery_percentage.png"), dpi=150)
    plt.close(fig)


def plot_volume(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(df["Date"], df["Total Traded Quantity"] / 1e7, color="tab:purple", linewidth=0.9)
    ax.set_xlabel("Date")
    ax.set_ylabel("Traded Quantity (Crore units)")
    ax.set_title("ITC: Daily Traded Volume")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "volume.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    df = load_data()
    plot_price_with_moving_averages(df)
    plot_drawdown(df)
    plot_delivery_pct(df)
    plot_volume(df)
    print(f"Figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
