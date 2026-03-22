import matplotlib.pyplot as plt
import numpy as np
import os

# Automatically detect folder and set save path
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'crude_oil_long_put_profile.png')

# Define Long Put Parameters based on actual March 17 execution
strike_price = 90
premium_paid = 4.98 
multiplier = 1000
quantity = 10

# Calculate Max Risk and Breakeven
max_loss = premium_paid * multiplier * quantity * -1
breakeven = strike_price - premium_paid

# Generate Crude Oil Prices for X-axis (from 75 to 100)
crude_prices = np.linspace(75, 100, 500)

# Calculate P&L at Expiration for the 10-lot position
pl = []
for price in crude_prices:
    put_value = max(strike_price - price, 0)
    total_pl = (put_value - premium_paid) * multiplier * quantity
    pl.append(total_pl)

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(crude_prices, pl, color='#1f77b4', linewidth=3, label='P&L at Expiration')

# Fill Profit and Loss areas
ax.fill_between(crude_prices, pl, 0, where=(np.array(pl) >= 0), color='#2ca02c', alpha=0.2)
ax.fill_between(crude_prices, pl, 0, where=(np.array(pl) < 0), color='#d62728', alpha=0.2)
ax.axhline(0, color='black', linewidth=1.5, linestyle='--')

# Highlight Strike and Breakeven
ax.axvline(strike_price, color='gray', linestyle=':', label=f'Put Strike ({strike_price})')
ax.axvline(breakeven, color='blue', linestyle='--', alpha=0.6, label=f'Breakeven ({breakeven:.2f})')

# Annotate the Max Risk boundary
ax.annotate(f'Hard-Capped Max Risk\n(-$49,800)', xy=(95, max_loss), xytext=(95, max_loss + 15000),
            arrowprops=dict(facecolor='red', shrink=0.05, width=1.5, headwidth=7),
            fontsize=11, fontweight='bold', color='darkred', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8))

# Formatting
ax.set_title('WTI Crude (CL) Long 90 Put Risk Profile', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('WTI Crude Price at Expiration ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Portfolio Profit / Loss (USD)', fontsize=12, fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(loc='upper right')

# Clean borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save and show
plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Success! Long Put risk profile chart saved to: {output_path}")
plt.show()