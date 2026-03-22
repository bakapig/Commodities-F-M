import matplotlib.pyplot as plt
import numpy as np
import os

# Automatically detect folder and set save path
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'gld_strangle_profile.png')

# Define Strangle Parameters based on Feb 6 CSV execution
call_strike = 460
put_strike = 435
call_premium = 8.21
put_premium = 11.38
net_debit = call_premium + put_premium  # 19.59 total
multiplier = 100

# Calculate Breakevens and Max Risk
max_loss = net_debit * multiplier * -1
upper_breakeven = call_strike + net_debit
lower_breakeven = put_strike - net_debit

# Generate GLD Prices for X-axis
gld_prices = np.linspace(400, 500, 500)

# Calculate P&L at Expiration
pl = []
for price in gld_prices:
    call_value = max(price - call_strike, 0)
    put_value = max(put_strike - price, 0)
    total_pl = (call_value + put_value - net_debit) * multiplier
    pl.append(total_pl)

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(gld_prices, pl, color='#9467bd', linewidth=3, label='P&L at Expiration')

# Fill Profit and Loss areas
ax.fill_between(gld_prices, pl, 0, where=(np.array(pl) >= 0), color='#2ca02c', alpha=0.2)
ax.fill_between(gld_prices, pl, 0, where=(np.array(pl) < 0), color='#d62728', alpha=0.2)
ax.axhline(0, color='black', linewidth=1.5, linestyle='--')

# Highlight Strikes
ax.axvline(call_strike, color='gray', linestyle=':', label=f'Call Strike ({call_strike})')
ax.axvline(put_strike, color='gray', linestyle=':', label=f'Put Strike ({put_strike})')

# Annotate the Successful Call Leg Exit
ax.annotate('Successful Exit (Feb 23)\nCall Leg Expanded', 
            xy=(479, 0), 
            xytext=(490, 1500),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=7),
            fontsize=11, fontweight='bold', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

# Formatting
ax.set_title('GLD Long Strangle (460 C / 435 P) Risk Profile', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('GLD ETF Price at Expiration ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Portfolio Profit / Loss (USD)', fontsize=12, fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(loc='upper right')

# Clean borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save and show
plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Success! GLD Strangle risk profile chart saved to: {output_path}")
plt.show()