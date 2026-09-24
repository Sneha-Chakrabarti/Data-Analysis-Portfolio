"""
Classifies each (Date, Symbol, Client) group as a "round trip" (client
bought and sold near-identical quantities of the same stock on the same
day, the signature of a quant/market-making desk providing liquidity) or
"directional" (a one-sided or clearly unbalanced position, the signature
of a genuine buy or sell decision). Aggregates client activity and saves
output/bulk_deals_analysis.csv, output/client_summary.csv, and
output/directional_net_flow.csv.
"""

import os
import numpy as np
import pandas as pd

from config import CLEANED_FILE, OUTPUT_DIR, ROUND_TRIP_QTY_MATCH_THRESHOLD


def classify_deals(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["Date", "Symbol", "Client Name"]

    for (date, symbol, client), group in df.groupby(group_cols):
        buy_rows = group[group["Buy / Sell"] == "BUY"]
        sell_rows = group[group["Buy / Sell"] == "SELL"]

        buy_qty = buy_rows["Quantity Traded"].sum()
        sell_qty = sell_rows["Quantity Traded"].sum()
        buy_value = buy_rows["Value"].sum()
        sell_value = sell_rows["Value"].sum()

        has_both = len(buy_rows) > 0 and len(sell_rows) > 0
        if has_both:
            match_ratio = min(buy_qty, sell_qty) / max(buy_qty, sell_qty)
            is_round_trip = match_ratio >= ROUND_TRIP_QTY_MATCH_THRESHOLD
        else:
            match_ratio = 0.0
            is_round_trip = False

        net_qty = buy_qty - sell_qty
        net_value = buy_value - sell_value
        total_value = buy_value + sell_value

        rows.append({
            "Date": date,
            "Symbol": symbol,
            "Client Name": client,
            "BuyQty": buy_qty,
            "SellQty": sell_qty,
            "BuyValue": buy_value,
            "SellValue": sell_value,
            "TotalValue": total_value,
            "NetQty": net_qty,
            "NetValue": net_value,
            "QtyMatchRatio": match_ratio,
            "Classification": "Round Trip" if is_round_trip else "Directional",
        })

    return pd.DataFrame(rows)


def client_summary(deals: pd.DataFrame) -> pd.DataFrame:
    summary = deals.groupby("Client Name").agg(
        TotalValue=("TotalValue", "sum"),
        DealCount=("TotalValue", "count"),
        RoundTripCount=("Classification", lambda s: (s == "Round Trip").sum()),
        DirectionalCount=("Classification", lambda s: (s == "Directional").sum()),
        DirectionalNetValue=("NetValue", lambda s: s[deals.loc[s.index, "Classification"] == "Directional"].sum()),
    ).reset_index()
    summary["RoundTripShare"] = summary["RoundTripCount"] / summary["DealCount"]
    return summary.sort_values("TotalValue", ascending=False)


def main():
    df = pd.read_csv(CLEANED_FILE, parse_dates=["Date"])
    deals = classify_deals(df)

    out_path = os.path.join(OUTPUT_DIR, "bulk_deals_analysis.csv")
    deals.to_csv(out_path, index=False)

    clients = client_summary(deals)
    clients_path = os.path.join(OUTPUT_DIR, "client_summary.csv")
    clients.to_csv(clients_path, index=False)

    directional_only = deals[deals["Classification"] == "Directional"].copy()
    net_flow = directional_only.groupby("Client Name")["NetValue"].sum().reset_index()
    net_flow = net_flow.sort_values("NetValue", ascending=False)
    net_flow_path = os.path.join(OUTPUT_DIR, "directional_net_flow.csv")
    net_flow.to_csv(net_flow_path, index=False)

    n_total = len(deals)
    n_round_trip = int((deals["Classification"] == "Round Trip").sum())
    n_directional = n_total - n_round_trip
    total_value = deals["TotalValue"].sum()
    round_trip_value = deals.loc[deals["Classification"] == "Round Trip", "TotalValue"].sum()

    print(f"Saved {n_total} client-stock-day groups to {out_path}")
    print(f"Saved client summary to {clients_path}")
    print(f"Saved directional net flow to {net_flow_path}\n")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"Total bulk deal value: Rs {total_value:,.0f}")
    print(f"Round trip groups: {n_round_trip}/{n_total} ({n_round_trip/n_total:.1%}), "
          f"accounting for Rs {round_trip_value:,.0f} ({round_trip_value/total_value:.1%} of value)")
    print(f"Directional groups: {n_directional}/{n_total} ({n_directional/n_total:.1%})")
    print("\nTop 10 clients by total traded value:")
    print(clients.head(10)[["Client Name", "TotalValue", "DealCount", "RoundTripShare"]].to_string(index=False))
    print("\nTop 5 net directional buyers:")
    print(net_flow.head(5).to_string(index=False))
    print("\nTop 5 net directional sellers:")
    print(net_flow.tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
