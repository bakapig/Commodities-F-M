import matplotlib.pyplot as plt
import os

# Automatically detect the folder to save the image
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'silver_curve_collapse.png')

# Define the contracts (Ticker months)
contracts = ['Front Month\n(APR)', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP']

# Entry Curve (Feb 23): Extreme Geopolitical Backwardation
entry_prices = [8550, 8400, 8250, 8100, 8000, 7950]

# Exit Curve (Mar 12): Panic Fading, Backwardation Collapsing
exit_prices = [8250, 8200, 8150, 8100, 8050, 8000]

# Create the figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the Futures Curves
ax.plot(contracts, entry_prices, marker='o', color='#d62728', linewidth=3, markersize=8, label='Feb 23: Extreme Backwardation (Put Spread Entry)')
ax.plot(contracts, exit_prices, marker='s', color='#1f77b4', linewidth=3, markersize=8, label='Mar 12: Curve Collapsing (Forced Exit)')

# Highlight the Short Strike (8400)
ax.axhline(y=8400, color='gray', linestyle='--', alpha=0.8, linewidth=1.5, label='Short Put Strike (8400)')

# Add an annotation showing the violent drop in the front month
ax.annotate('Front-Month\nPremium Collapse', 
            xy=(0, 8270), 
            xytext=(0.5, 8450),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=7),
            fontsize=11, fontweight='bold', ha='left',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

# Formatting
ax.set_title('Silver Futures Term Structure: The Backwardation Collapse', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Futures Contract Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Contract Price ($/oz)', fontsize=12, fontweight='bold')
ax.set_ylim(7800, 8700)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='lower left', fontsize=10)

# Clean borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save the plot explicitly to the script's directory
plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Success! Silver term structure chart saved to: {output_path}")

plt.show()