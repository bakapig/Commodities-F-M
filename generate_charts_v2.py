"""
Professional PnL Chart Suite — IBKR Trading Portfolio
Generates 8 investment-analyst-grade charts from IBKR CSV exports.
"""

import pandas as pd
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib import patheffects
import os
import re

# Ensure stdout can handle UTF-8 on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from collections import defaultdict

# ──────────────────────────── CONFIG ──────────────────────────── #
OUTPUT_DIR = r"c:\Users\admin\Desktop\FE5227\Charts"
TXN_FILE   = r"c:\Users\admin\Desktop\FE5227\DUO116877.TRANSACTIONS.YTD.csv"
STMT_FILE  = r"c:\Users\admin\Desktop\FE5227\DUO116877_20260128_20260320.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

STARTING_NAV = 1_000_000.0

# ──────────────────── THEME & PALETTE ──────────────────── #
BG        = "#ffffff"
CARD_BG   = "#f6f8fa"
GRID_CLR  = "#d0d7de"
TEXT_CLR  = "#1f2328"
MUTED     = "#656d76"
GREEN     = "#1a7f37"
RED       = "#cf222e"
TEAL      = "#0969da"
CORAL     = "#bc4c00"
AMBER     = "#9a6700"
PURPLE    = "#8250df"
CYAN      = "#0a7d6c"
PINK      = "#bf3989"
ORANGE    = "#d4740e"
BLUE2     = "#0550ae"

PALETTE = [TEAL, CORAL, AMBER, PURPLE, CYAN, PINK, ORANGE, BLUE2, GREEN, RED]

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
    "axes.edgecolor":   GRID_CLR,
    "axes.labelcolor":  TEXT_CLR,
    "text.color":       TEXT_CLR,
    "xtick.color":      MUTED,
    "ytick.color":      MUTED,
    "grid.color":       GRID_CLR,
    "grid.linestyle":   "--",
    "grid.alpha":       0.35,
    "font.family":      "sans-serif",
    "font.size":        11,
    "legend.facecolor": BG,
    "legend.edgecolor": GRID_CLR,
    "legend.fontsize":  9,
})


def fmt_usd(x, pos=None):
    """Format number as USD with K/M suffix."""
    if abs(x) >= 1e6:
        return f"${x/1e6:,.1f}M"
    if abs(x) >= 1e3:
        return f"${x/1e3:,.0f}K"
    return f"${x:,.0f}"


def fmt_usd_full(x):
    return f"${x:,.2f}"


# ──────────────────── DATA PARSING ──────────────────── #
print("[*] Loading data...")

# ──── Transaction History (YTD file) ──── #
txn_lines = open(TXN_FILE, "r").readlines()

txn_rows = []
for line in txn_lines:
    parts = line.strip().split(",")
    if len(parts) < 13:
        continue
    if parts[0] == "Transaction History" and parts[1] == "Data":
        date_str = parts[2].strip()
        desc     = parts[4].strip()
        txn_type = parts[5].strip()
        symbol   = parts[6].strip()
        net_amt_str = parts[12].strip()
        try:
            net_amt = float(net_amt_str)
        except (ValueError, IndexError):
            continue
        try:
            date = pd.to_datetime(date_str)
        except:
            continue
        txn_rows.append({
            "Date": date,
            "Description": desc,
            "Type": txn_type,
            "Symbol": symbol,
            "Net Amount": net_amt,
        })

df_txn = pd.DataFrame(txn_rows)

# ──── Activity Statement ──── #
stmt_lines = open(STMT_FILE, "r").readlines()

# Parse Realized & Unrealized Performance Summary (My Investments section — after line 375)
perf_rows = []
in_my_investments = False
for i, line in enumerate(stmt_lines):
    parts = line.strip().split(",")
    if len(parts) < 2:
        continue
    # The second "Realized & Unrealized Performance Summary" section starts after the second Statement header
    if i > 300 and parts[0] == "Realized & Unrealized Performance Summary" and parts[1] == "Data":
        if len(parts) >= 16:
            cat   = parts[2].strip()
            sym   = parts[3].strip()
            if cat in ("Total", "Total (All Assets)") or not sym:
                continue
            try:
                realized_total  = float(parts[9]) if parts[9] else 0
                unrealized_total = float(parts[14]) if parts[14] else 0
                total_pnl       = float(parts[15]) if parts[15] else 0
            except (ValueError, IndexError):
                continue
            perf_rows.append({
                "Asset Category": cat,
                "Symbol": sym,
                "Realized P/L": realized_total,
                "Unrealized P/L": unrealized_total,
                "Total P/L": total_pnl,
            })

df_perf = pd.DataFrame(perf_rows)

# Parse Trades section for individual trade data (My Investments section — after line 486)
trade_rows = []
for i, line in enumerate(stmt_lines):
    parts = line.strip().split(",")
    if len(parts) < 16:
        continue
    if i > 480 and parts[0] == "Trades" and parts[1] == "Data" and parts[2] == "Order":
        cat      = parts[3].strip()
        currency = parts[4].strip()
        symbol   = parts[5].strip()
        date_str = parts[6].strip().strip('"')
        try:
            realized_pnl = float(parts[13]) if parts[13] else 0
        except (ValueError, IndexError):
            realized_pnl = 0
        try:
            date = pd.to_datetime(date_str)
        except:
            continue
        trade_rows.append({
            "Date": date,
            "Category": cat,
            "Symbol": symbol,
            "Realized P/L": realized_pnl,
        })

df_trades = pd.DataFrame(trade_rows)

# ──── Commodity Group Mapping ──── #
def get_commodity_group(symbol):
    s = symbol.upper()
    if any(x in s for x in ["GC", "OG", "G4W", "GOLD", "GLD"]):
        return "Gold"
    if any(x in s for x in ["SI", "SO", "SILVER"]):
        return "Silver"
    if any(x in s for x in ["CC", "CO", "COCOA"]):
        return "Cocoa"
    if any(x in s for x in ["ZS", "OZS", "SOYBEAN"]):
        return "Soybeans"
    if any(x in s for x in ["FCPO", "PALM"]):
        return "Palm Oil"
    if any(x in s for x in ["PA", "PALLADIUM"]):
        return "Palladium"
    if any(x in s for x in ["PL", "PLATINUM"]):
        return "Platinum"
    if any(x in s for x in ["TFM"]):
        return "TTF Dutch Gas"
    if any(x in s for x in ["NG", "LNE", "NATGAS"]):
        return "Henry Hub"
    if any(x in s for x in ["CL", "ML5", "CRUDE"]):
        return "Crude Oil"
    if any(x in s for x in ["SB", "SUGAR"]):
        return "Sugar"
    return "Other"


GROUP_COLORS = {
    "Gold": "#FFD700",
    "Silver": "#C0C0C0",
    "Cocoa": "#8B4513",
    "Soybeans": "#228B22",
    "Palm Oil": "#FF8C00",
    "Palladium": "#BC8F8F",
    "Platinum": "#E5E4E2",
    "Platinum": "#E5E4E2",
    "TTF Dutch Gas": TEAL,
    "Henry Hub": CORAL,
    "Crude Oil": "#4169E1",
    "Sugar": PINK,
    "Other": MUTED,
}

print(f"  ✓ {len(df_txn)} transaction rows parsed")
print(f"  ✓ {len(df_perf)} performance summary rows parsed")
print(f"  ✓ {len(df_trades)} trade rows parsed")


# ═══════════════════════════════════════════════════════════════ #
#                           CHART 1                              #
#       Portfolio NAV & Cumulative PnL Over Time                 #
# ═══════════════════════════════════════════════════════════════ #
print("📊 Chart 1: Portfolio NAV & Cumulative PnL Over Time...")

# Filter out internal transfers (deposits/withdrawals to sub-accounts)
df_nav = df_txn[~df_txn["Type"].isin(["Deposit", "Withdrawal"])].copy()
daily_pnl = df_nav.groupby("Date")["Net Amount"].sum().sort_index()
cum_pnl   = daily_pnl.cumsum()
nav_ts    = STARTING_NAV + cum_pnl
pct_ts    = (cum_pnl / STARTING_NAV) * 100

fig, ax1 = plt.subplots(figsize=(14, 6))
ax2 = ax1.twinx()

# NAV line
ax1.fill_between(nav_ts.index, STARTING_NAV, nav_ts.values, alpha=0.15, color=TEAL)
ax1.plot(nav_ts.index, nav_ts.values, color=TEAL, linewidth=2.5, label="Portfolio NAV")
ax1.axhline(STARTING_NAV, color=MUTED, linewidth=0.8, linestyle=":", alpha=0.6)

# PnL % line
ax2.plot(pct_ts.index, pct_ts.values, color=CORAL, linewidth=1.5, linestyle="--", alpha=0.8, label="Cumulative PnL %")
ax2.axhline(0, color=MUTED, linewidth=0.8, linestyle=":", alpha=0.6)

# Annotations
ax1.annotate(f"Start: {fmt_usd(STARTING_NAV)}", xy=(nav_ts.index[0], STARTING_NAV),
             fontsize=9, color=MUTED, ha="left", va="bottom",
             xytext=(10, 10), textcoords="offset points")
end_val = nav_ts.iloc[-1]
end_pct = pct_ts.iloc[-1]
c = GREEN if end_pct >= 0 else RED
ax1.annotate(f"End: {fmt_usd(end_val)} ({end_pct:+.1f}%)", xy=(nav_ts.index[-1], end_val),
             fontsize=10, fontweight="bold", color=c, ha="right", va="top",
             xytext=(-10, -15), textcoords="offset points",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=BG, edgecolor=c, alpha=0.9))

ax1.set_ylabel("Portfolio NAV (USD)", fontsize=12, fontweight="bold")
ax2.set_ylabel("Cumulative PnL (%)", fontsize=12, fontweight="bold", color=CORAL)
ax1.set_title("Portfolio NAV & Cumulative PnL Over Time", fontsize=16, fontweight="bold", pad=15)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_usd))
ax2.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
ax1.grid(True)
ax1.tick_params(axis="x", rotation=30)

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", framealpha=0.9)

fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "01_NAV_Cumulative_PnL.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
#                           CHART 2                              #
#              PnL by Instrument (Horizontal Bar)                #
# ═══════════════════════════════════════════════════════════════ #
print("📊 Chart 2: PnL by Instrument...")

df_inst = df_perf.sort_values("Total P/L", ascending=True).copy()
colors2 = [GREEN if x >= 0 else RED for x in df_inst["Total P/L"]]

fig, ax = plt.subplots(figsize=(13, max(7, len(df_inst) * 0.45)))
bars = ax.barh(df_inst["Symbol"], df_inst["Total P/L"], color=colors2, edgecolor=[c + "66" for c in colors2], linewidth=0.5, height=0.7)

# Value labels
for bar, val in zip(bars, df_inst["Total P/L"]):
    x_pos = bar.get_width()
    ha = "left" if val >= 0 else "right"
    offset = 200 if val >= 0 else -200
    ax.text(x_pos + offset, bar.get_y() + bar.get_height() / 2,
            fmt_usd(val), va="center", ha=ha, fontsize=8, color=TEXT_CLR, fontweight="bold")

ax.axvline(0, color=MUTED, linewidth=0.8)
ax.set_title("Total P&L by Traded Instrument", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Profit / Loss (USD)", fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_usd))
ax.grid(axis="x")

fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "02_PnL_by_Instrument.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
# ═══════════════════════════════════════════════════════════════ #
#                           CHART 3                              #
#       PnL Breakdown by Asset Class (Horizontal Grouped Bar)    #
# ═══════════════════════════════════════════════════════════════ #
print("📊 Chart 3: PnL by Asset Class...")

cat_data = df_perf.groupby("Asset Category").agg(
    Realized=("Realized P/L", "sum"),
    Unrealized=("Unrealized P/L", "sum"),
    Total=("Total P/L", "sum")
).sort_values("Total", ascending=True)

fig, ax = plt.subplots(figsize=(12, 6))
y = np.arange(len(cat_data))
h = 0.28

bars1 = ax.barh(y - h, cat_data["Realized"], h, label="Realized P/L", color=TEAL, edgecolor=TEAL + "88", linewidth=0.5)
bars2 = ax.barh(y,     cat_data["Unrealized"], h, label="Unrealized P/L", color=AMBER, edgecolor=AMBER + "88", linewidth=0.5)
bars3 = ax.barh(y + h, cat_data["Total"], h, label="Total P/L", color=CORAL, edgecolor=CORAL + "88", linewidth=0.5)

ax.set_yticks(y)
ax.set_yticklabels(cat_data.index, fontsize=11, fontweight="bold")
ax.axvline(0, color=MUTED, linewidth=0.8)
ax.set_title("P&L Breakdown by Asset Class", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Profit / Loss (USD)", fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_usd))
ax.legend(loc="lower left", framealpha=0.9)
ax.grid(axis="x")

# Value labels on Total bars
for bar, val in zip(bars3, cat_data["Total"]):
    x_pos = bar.get_width()
    ha = "left" if val >= 0 else "right"
    ax.annotate(fmt_usd(val), xy=(x_pos, bar.get_y() + bar.get_height() / 2),
                xytext=(6 if val >= 0 else -6, 0), textcoords="offset points",
                ha=ha, va="center", fontsize=9, fontweight="bold", color=GREEN if val >= 0 else RED)

ax.margins(x=0.15)
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "03_PnL_by_Asset_Class.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
#                           CHART 4                              #
#            Top 5 Winners & Top 5 Losers                        #
# ═══════════════════════════════════════════════════════════════ #
print("📊 Chart 4: Top 5 Winners & Losers...")

df_sorted = df_perf.sort_values("Total P/L")
n_show = min(5, len(df_sorted))
df_top_bottom = pd.concat([df_sorted.head(n_show), df_sorted.tail(n_show)]).drop_duplicates().sort_values("Total P/L")

fig, ax = plt.subplots(figsize=(14, max(6, len(df_top_bottom) * 0.7)))
colors4 = [GREEN if x >= 0 else RED for x in df_top_bottom["Total P/L"]]
bars = ax.barh(df_top_bottom["Symbol"], df_top_bottom["Total P/L"], color=colors4,
               edgecolor=[c + "55" for c in colors4], linewidth=0.5, height=0.65)

for bar, val in zip(bars, df_top_bottom["Total P/L"]):
    x_pos = bar.get_width()
    ha = "left" if val >= 0 else "right"
    ax.annotate(fmt_usd_full(val), xy=(x_pos, bar.get_y() + bar.get_height() / 2),
                xytext=(8 if val >= 0 else -8, 0), textcoords="offset points",
                ha=ha, va="center", fontsize=11, color=TEXT_CLR, fontweight="bold")

ax.axvline(0, color=MUTED, linewidth=1)
ax.set_title("Top 5 Winners vs Top 5 Losers", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Total P&L (USD)", fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_usd))
ax.grid(axis="x")
ax.margins(x=0.2)

# Add winner/loser labels
ax.text(0.98, 0.98, "+ WINNERS", transform=ax.transAxes, fontsize=12, fontweight="bold",
        color=GREEN, ha="right", va="top")
ax.text(0.02, 0.02, "- LOSERS", transform=ax.transAxes, fontsize=12, fontweight="bold",
        color=RED, ha="left", va="bottom")

fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "04_Top_Bottom_Winners_Losers.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
#                           CHART 5                              #
#        PnL Heatmap by Week × Commodity Group                   #
# ═══════════════════════════════════════════════════════════════ #
print("📊 Chart 5: PnL Heatmap by Week × Commodity Group...")

# Use transaction data for weekly breakdown
df_heat = df_txn[~df_txn["Type"].isin(["Deposit", "Withdrawal", "Credit Interest"])].copy()
df_heat["Group"] = df_heat["Symbol"].apply(get_commodity_group)
df_heat["Week"] = df_heat["Date"].dt.isocalendar().week.astype(int)
df_heat["Year_Week"] = df_heat["Date"].dt.strftime("W%V")

heat_pivot = df_heat.groupby(["Group", "Year_Week"])["Net Amount"].sum().unstack(fill_value=0)
# Sort columns chronologically
week_order = sorted(heat_pivot.columns, key=lambda w: int(w[1:]))
heat_pivot = heat_pivot.reindex(columns=week_order)

# Remove "Other" group if it exists and is empty
if "Other" in heat_pivot.index and heat_pivot.loc["Other"].abs().sum() < 1:
    heat_pivot = heat_pivot.drop("Other")

fig, ax = plt.subplots(figsize=(max(12, len(heat_pivot.columns) * 1.2), max(5, len(heat_pivot) * 0.7)))

# Custom diverging colormap
from matplotlib.colors import LinearSegmentedColormap
div_cmap = LinearSegmentedColormap.from_list("pnl_div", [RED, "#1a1a2e", GREEN])

vmax = max(abs(heat_pivot.values.min()), abs(heat_pivot.values.max()))
im = ax.imshow(heat_pivot.values, cmap=div_cmap, aspect="auto", vmin=-vmax, vmax=vmax)

ax.set_xticks(range(len(heat_pivot.columns)))
ax.set_xticklabels(heat_pivot.columns, rotation=45, ha="right", fontsize=9)
ax.set_yticks(range(len(heat_pivot.index)))
ax.set_yticklabels(heat_pivot.index, fontsize=10)

# Add text annotations
for i in range(len(heat_pivot.index)):
    for j in range(len(heat_pivot.columns)):
        val = heat_pivot.values[i, j]
        if abs(val) > 50:
            txt = f"${val/1e3:+.1f}K" if abs(val) >= 1000 else f"${val:+.0f}"
            text_color = "#ffffff" if abs(val) > vmax * 0.3 else MUTED
            ax.text(j, i, txt, ha="center", va="center", fontsize=7, color=text_color, fontweight="bold")

cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("P&L (USD)", fontsize=10, color=TEXT_CLR)
cbar.ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_usd))

ax.set_title("Weekly P&L Heatmap by Commodity Group", fontsize=16, fontweight="bold", pad=15)
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "05_Weekly_PnL_Heatmap.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
#                           CHART 6                              #
#         Win Rate & Trade Statistics (Donut + KPIs)             #
# ═══════════════════════════════════════════════════════════════ #
print("📊 Chart 6: Win Rate & Trade Statistics...")

# Only look at closed trades (those with non-zero realized PnL)
closed = df_trades[df_trades["Realized P/L"] != 0].copy()
n_wins  = (closed["Realized P/L"] > 0).sum()
n_losses = (closed["Realized P/L"] < 0).sum()
total_trades = n_wins + n_losses
win_rate = n_wins / total_trades * 100 if total_trades > 0 else 0

wins_df   = closed[closed["Realized P/L"] > 0]["Realized P/L"]
losses_df = closed[closed["Realized P/L"] < 0]["Realized P/L"]
avg_win  = wins_df.mean() if len(wins_df) > 0 else 0
avg_loss = losses_df.mean() if len(losses_df) > 0 else 0
max_win  = wins_df.max() if len(wins_df) > 0 else 0
max_loss = losses_df.min() if len(losses_df) > 0 else 0
profit_factor = abs(wins_df.sum() / losses_df.sum()) if losses_df.sum() != 0 else float("inf")

fig = plt.figure(figsize=(16, 8))
gs = GridSpec(1, 2, width_ratios=[1, 1.5], figure=fig)

# Donut chart
ax_donut = fig.add_subplot(gs[0])
sizes = [n_wins, n_losses]
colors_d = [GREEN, RED]
explode = (0.03, 0.03)
wedges, texts, autotexts = ax_donut.pie(
    sizes, explode=explode, colors=colors_d, autopct="%1.1f%%",
    startangle=90, pctdistance=0.75, textprops={"fontsize": 13, "fontweight": "bold", "color": TEXT_CLR}
)
centre_circle = plt.Circle((0, 0), 0.55, fc=BG)
ax_donut.add_artist(centre_circle)
ax_donut.text(0, 0.08, f"{total_trades}", fontsize=28, fontweight="bold", ha="center", va="center", color=TEXT_CLR)
ax_donut.text(0, -0.15, "trades", fontsize=11, ha="center", va="center", color=MUTED)
ax_donut.set_title("Win / Loss Distribution", fontsize=14, fontweight="bold", pad=10)
ax_donut.legend([f"Winners ({n_wins})", f"Losers ({n_losses})"], loc="lower center",
                fontsize=10, framealpha=0.9, ncol=2)

# KPI Cards
ax_kpi = fig.add_subplot(gs[1])
ax_kpi.axis("off")

kpis = [
    ("Win Rate",       f"{win_rate:.1f}%",          GREEN if win_rate >= 50 else RED),
    ("Avg Win",        fmt_usd_full(avg_win),        GREEN),
    ("Avg Loss",       fmt_usd_full(avg_loss),       RED),
    ("Profit Factor",  f"{profit_factor:.2f}x",      GREEN if profit_factor > 1 else RED),
    ("Max Win",        fmt_usd_full(max_win),         GREEN),
    ("Max Loss",       fmt_usd_full(max_loss),        RED),
]

for i, (label, value, color) in enumerate(kpis):
    row = i // 3
    col = i % 3
    x = 0.05 + col * 0.33
    y = 0.75 - row * 0.45

    # Card background
    rect = mpatches.FancyBboxPatch((x - 0.02, y - 0.15), 0.29, 0.35,
                                    boxstyle="round,pad=0.02", facecolor=CARD_BG, edgecolor=GRID_CLR, linewidth=1)
    ax_kpi.add_patch(rect)
    ax_kpi.text(x + 0.125, y + 0.12, label, fontsize=11, ha="center", va="center",
                color=MUTED, fontweight="bold", transform=ax_kpi.transAxes)
    ax_kpi.text(x + 0.125, y - 0.02, value, fontsize=18, ha="center", va="center",
                color=color, fontweight="bold", transform=ax_kpi.transAxes)

ax_kpi.set_xlim(0, 1)
ax_kpi.set_ylim(0, 1)

# Add explanatory text for the KPIs below the cards
explanation = (
    "Glossary:\n"
    "• Win Rate: Percentage of profitable trades out of all closed trades.\n"
    "• Avg Win / Avg Loss: The average amount made on winning trades vs lost on losing trades.\n"
    "• Profit Factor: Gross Winning P&L divided by Gross Losing P&L. >1.0 indicates a profitable strategy.\n"
    "• Max Win / Max Loss: The single largest profit and loss recorded in a closed trade."
)
ax_kpi.text(0.5, 0.10, explanation, fontsize=10, ha="center", va="top",
            color=MUTED, transform=ax_kpi.transAxes, style="italic",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=BG, edgecolor=GRID_CLR, alpha=0.9))


fig.suptitle("Trade Statistics & Win Rate Analysis", fontsize=18, fontweight="bold", y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(os.path.join(OUTPUT_DIR, "06_Win_Rate_Statistics.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
#                           CHART 7                              #
#     Cumulative Realized PnL by Commodity Group Over Time       #
# ═══════════════════════════════════════════════════════════════ #
print("Chart 7: Cumulative PnL by Commodity Group...")

df_grp = df_txn[~df_txn["Type"].isin(["Deposit", "Withdrawal", "Credit Interest"])].copy()
df_grp["Group"] = df_grp["Symbol"].apply(get_commodity_group)
df_grp = df_grp[df_grp["Group"] != "Other"]

groups_present = sorted(df_grp["Group"].unique())

# Build a cumulative series per group, aligned to a common date index
cum_series = {}
for grp in groups_present:
    subset = df_grp[df_grp["Group"] == grp].groupby("Date")["Net Amount"].sum().sort_index().cumsum()
    cum_series[grp] = subset

# Create common date index spanning the full period
all_dates = sorted(set().union(*(s.index for s in cum_series.values())))
for grp in cum_series:
    cum_series[grp] = cum_series[grp].reindex(all_dates).ffill().fillna(0)

# Sort groups by final cumulative value (best performers on top in legend)
sorted_groups = sorted(cum_series.keys(), key=lambda g: cum_series[g].iloc[-1], reverse=True)

fig, ax = plt.subplots(figsize=(20, 12))

# 1. Gather endpoint values to calculate anti-overlap label positions
end_points = []
for grp in sorted_groups:
    series = cum_series[grp]
    if len(series) > 0:
        end_points.append({"grp": grp, "true_y": series.iloc[-1], "adj_y": series.iloc[-1]})

# Sort by Y value
end_points.sort(key=lambda x: x["true_y"])

# 2. Relax Y positions to prevent overlap
data_max = max(p["true_y"] for p in end_points) if end_points else 0
data_min = min(p["true_y"] for p in end_points) if end_points else 0
data_range = data_max - data_min if data_max != data_min else 1000
min_sep = data_range * 0.045 # 4.5% vertical separation minimum

for _ in range(100):
    for i in range(len(end_points) - 1):
        diff = end_points[i+1]["adj_y"] - end_points[i]["adj_y"]
        if diff < min_sep:
            overlap = min_sep - diff
            end_points[i]["adj_y"] -= overlap / 2
            end_points[i+1]["adj_y"] += overlap / 2

adj_y_map = {p["grp"]: p["adj_y"] for p in end_points}
true_y_map = {p["grp"]: p["true_y"] for p in end_points}

# 3. Plot lines and adjusted labels
for idx, grp in enumerate(sorted_groups):
    series = cum_series[grp]
    color = GROUP_COLORS.get(grp, PALETTE[idx % len(PALETTE)])

    # Line with subtle area fill
    ax.plot(series.index, series.values, linewidth=2.5, label=f"{grp}  ({fmt_usd(series.iloc[-1])})",
            color=color, zorder=3)
    ax.fill_between(series.index, 0, series.values, color=color, alpha=0.08, zorder=1)

    # Clean end label with background box
    if len(series) > 0:
        true_y = true_y_map[grp]
        adj_y = adj_y_map[grp]
        last_date = series.index[-1]
        text_x = last_date + pd.Timedelta(days=1.8) # Push text out by 1.8 days
        
        ax.annotate(
            f" {grp} ",
            xy=(last_date, true_y),
            xytext=(text_x, adj_y),
            textcoords="data",
            fontsize=9.5, color=color, fontweight="bold", va="center",
            bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec=color, alpha=0.9, linewidth=0.8),
            arrowprops=dict(arrowstyle="-", color=color, lw=0.9, alpha=0.8)
        )

# Ensure enough space on the right for the text labels
if len(end_points) > 0:
    ax.set_xlim(right=last_date + pd.Timedelta(days=15))

# Zero line
ax.axhline(0, color=TEXT_CLR, linewidth=0.9, linestyle="-", alpha=0.3, zorder=2)

ax.set_title("Cumulative P&L by Commodity Group Over Time", fontsize=19, fontweight="bold", pad=20)
ax.set_ylabel("Cumulative P&L (USD)", fontsize=13, fontweight="bold")
ax.yaxis.set_major_locator(mticker.MultipleLocator(50000)) # Force 50k ticks
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_usd))
ax.grid(True, alpha=0.35)
ax.tick_params(axis="x", rotation=30, labelsize=11)
ax.tick_params(axis="y", labelsize=11)

# Legend sorted by performance, outside the plot area
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=min(5, len(sorted_groups)),
          framealpha=0.95, fontsize=11, columnspacing=1.8, handlelength=3)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "07_Cumulative_PnL_by_Group.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
#                           CHART 8                              #
#           Portfolio Summary Dashboard (KPI Banner)             #
# ═══════════════════════════════════════════════════════════════ #
print("📊 Chart 8: Portfolio Summary Dashboard...")

ending_nav = 549_839.44
total_return_pct = ((ending_nav - STARTING_NAV) / STARTING_NAV) * 100
total_realized = df_perf["Realized P/L"].sum()
total_unrealized = df_perf["Unrealized P/L"].sum()
total_commissions = -1066.94  # from statement
total_pnl = df_perf["Total P/L"].sum()

fig, ax = plt.subplots(figsize=(16, 5))
ax.axis("off")
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Title banner
ax.text(0.5, 0.95, "PORTFOLIO PERFORMANCE SUMMARY", fontsize=22, fontweight="bold",
        ha="center", va="top", color=TEXT_CLR, transform=ax.transAxes,
        path_effects=[patheffects.withStroke(linewidth=2, foreground="#ffffff")])
ax.text(0.5, 0.82, "Jan 28 – Mar 20, 2026  •  IBKR Account DUO116877",
        fontsize=11, ha="center", va="top", color=MUTED, transform=ax.transAxes)

# Horizontal rule (use plot since axhline doesn't accept transform)
ax.plot([0.05, 0.95], [0.75, 0.75], color=GRID_CLR, linewidth=1, transform=ax.transAxes, clip_on=False)

kpis_dash = [
    ("Starting NAV",    fmt_usd_full(STARTING_NAV),      TEXT_CLR),
    ("Ending NAV",      fmt_usd_full(ending_nav),         RED if ending_nav < STARTING_NAV else GREEN),
    ("Total Return",    f"{total_return_pct:+.2f}%",      RED if total_return_pct < 0 else GREEN),
    ("Realized P/L",    fmt_usd_full(total_realized),     RED if total_realized < 0 else GREEN),
    ("Unrealized P/L",  fmt_usd_full(total_unrealized),   RED if total_unrealized < 0 else GREEN),
    ("Commissions",     fmt_usd_full(total_commissions),  RED),
]

ncols = len(kpis_dash)
for i, (label, value, color) in enumerate(kpis_dash):
    x = 0.08 + i * (0.86 / ncols)

    # Card box
    rect = mpatches.FancyBboxPatch((x - 0.01, 0.15), 0.86 / ncols - 0.015, 0.52,
                                    boxstyle="round,pad=0.015", facecolor=CARD_BG, edgecolor=GRID_CLR,
                                    linewidth=1.2, transform=ax.transAxes)
    ax.add_patch(rect)

    ax.text(x + (0.86 / ncols - 0.015) / 2, 0.58, label,
            fontsize=9, ha="center", va="center", color=MUTED, fontweight="bold",
            transform=ax.transAxes)
    ax.text(x + (0.86 / ncols - 0.015) / 2, 0.38, value,
            fontsize=15, ha="center", va="center", color=color, fontweight="bold",
            transform=ax.transAxes)

# Bottom note
ax.text(0.5, 0.05, "Data source: Interactive Brokers Activity Statement & Transaction History",
        fontsize=8, ha="center", va="center", color=MUTED, style="italic", transform=ax.transAxes)

fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "08_Portfolio_Summary_Dashboard.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
#                           CHART 9                              #
#              PnL by Commodity Group (Horizontal Bar)           #
# ═══════════════════════════════════════════════════════════════ #
print("📊 Chart 9: PnL by Commodity Group...")

df_group_pnl = df_perf.copy()
df_group_pnl["Group"] = df_group_pnl["Symbol"].apply(get_commodity_group)
grouped_pnl = df_group_pnl.groupby("Group")["Total P/L"].sum().sort_values(ascending=True)

colors9 = [GREEN if x >= 0 else RED for x in grouped_pnl]

fig, ax = plt.subplots(figsize=(13, max(6, len(grouped_pnl) * 0.6)))
bars = ax.barh(grouped_pnl.index, grouped_pnl.values, color=colors9, edgecolor=[c + "66" for c in colors9], linewidth=0.5, height=0.6)

# Value labels
for bar, val in zip(bars, grouped_pnl.values):
    x_pos = bar.get_width()
    ha = "left" if val >= 0 else "right"
    ax.annotate(fmt_usd(val), xy=(x_pos, bar.get_y() + bar.get_height() / 2),
                xytext=(8 if val >= 0 else -8, 0), textcoords="offset points",
                ha=ha, va="center", fontsize=10, color=TEXT_CLR, fontweight="bold")

ax.axvline(0, color=MUTED, linewidth=0.8)
ax.set_title("Total P&L by Commodity Group", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Profit / Loss (USD)", fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_usd))
ax.grid(axis="x")
ax.margins(x=0.15)

fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "09_PnL_by_Commodity_Group.png"), dpi=300, bbox_inches="tight")
plt.close(fig)


# ═══════════════════════════════════════════════════════════════ #
print(f"\n✅ All 9 charts generated successfully in: {OUTPUT_DIR}")
print("   01_NAV_Cumulative_PnL.png")
print("   02_PnL_by_Instrument.png")
print("   03_PnL_by_Asset_Class.png")
print("   04_Top_Bottom_Winners_Losers.png")
print("   05_Weekly_PnL_Heatmap.png")
print("   06_Win_Rate_Statistics.png")
print("   07_Cumulative_PnL_by_Group.png")
print("   08_Portfolio_Summary_Dashboard.png")
print("   09_PnL_by_Commodity_Group.png")
