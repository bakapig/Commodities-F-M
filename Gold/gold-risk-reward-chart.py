import matplotlib.pyplot as plt
import numpy as np
import os

# Automatically detect folder and set save path
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'gold_bull_call_profile.png')

# Define Bull Call Spread Parameters based on actual screenshots
long_strike = 5350
short_strike = 5450
net_debit = 23.40
multiplier = 100
quantity = 10

# Calculate Max Risk, Max Profit, and Breakeven
max_loss = net_debit * multiplier * quantity * -1
max_profit = ((short_strike - long_strike) - net_debit) * multiplier * quantity
breakeven = long_strike + net_debit

# Generate Gold Prices for X-axis
gold_prices = np.linspace(5250, 5550, 500)

# Calculate P&L at Expiration for the 10-lot position
pl = []
for price in gold_prices:
    long_call_value = max(price - long_strike, 0)
    short_call_value = max(price - short_strike, 0) * -1
    total_pl = (long_call_value + short_call_value - net_debit) * multiplier * quantity
    pl.append(total_pl)

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(gold_prices, pl, color='#1f77b4', linewidth=3, label='P&L at Expiration')

# Fill Profit and Loss areas
ax.fill_between(gold_prices, pl, 0, where=(np.array(pl) >= 0), color='#2ca02c', alpha=0.2)
ax.fill_between(gold_prices, pl, 0, where=(np.array(pl) < 0), color='#d62728', alpha=0.2)
ax.axhline(0, color='black', linewidth=1.5, linestyle='--')

# Highlight Strikes and Breakeven
ax.axvline(long_strike, color='gray', linestyle=':', label=f'Long Strike ({long_strike})')
ax.axvline(short_strike, color='gray', linestyle=':', label=f'Short Strike ({short_strike})')
ax.axvline(breakeven, color='blue', linestyle='--', alpha=0.6, label=f'Breakeven ({breakeven:.2f})')

# Annotate Max Profit and Risk
ax.annotate(f'Max Reward\n(+$76,600)', xy=(5480, max_profit), xytext=(5480, max_profit - 20000),
            arrowprops=dict(facecolor='green', shrink=0.05, width=1.5, headwidth=7),
            fontsize=11, fontweight='bold', color='darkgreen', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="green", alpha=0.8))

ax.annotate(f'Max Risk\n(-$23,400)', xy=(5300, max_loss), xytext=(5300, max_loss + 20000),
            arrowprops=dict(facecolor='red', shrink=0.05, width=1.5, headwidth=7),
            fontsize=11, fontweight='bold', color='darkred', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8))

# Formatting
ax.set_title('Gold (GC) 5350 / 5450 Bull Call Spread Risk Profile', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Gold Price at Expiration ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Portfolio Profit / Loss (USD)', fontsize=12, fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(loc='upper left')

# Clean borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save and show
plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Success! Gold risk profile chart saved to: {output_path}")
plt.show()