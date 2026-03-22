import matplotlib.pyplot as plt
import os

# Automatically detect the folder to save the image
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'ng_futures_curve.png')

# Define the contracts (Ticker months)
contracts = ['Jan (F)', 'Feb (G)', 'Mar (H)', 'Apr (J)', 'May (K)', 'Jun (M)']
# Example Prices (showing backwardation from Feb to Mar/Apr)
prices = [3.85, 3.90, 3.40, 2.75, 2.80, 2.95]

# Create the figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the Futures Curve
ax.plot(contracts, prices, marker='o', color='#d62728', linewidth=3, markersize=8)

# Highlight the Structural Drop (March to April)
ax.annotate('Structural March-April Drop\n(Transition to Shoulder Season)', 
            xy=(3, 2.75), 
            xytext=(2.5, 3.6),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=7),
            fontsize=11, fontweight='bold', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

# Add a dashed line showing the spot price / front month baseline
ax.axhline(y=3.85, color='gray', linestyle='--', alpha=0.5, label='Front Month Baseline')

# Formatting
ax.set_title('Natural Gas Futures Curve (Term Structure)', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Futures Contract Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Contract Price ($/mmBtu)', fontsize=12, fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.6)

# Clean borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save the plot explicitly to the script's directory
plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Success! Professional futures curve chart saved to: {output_path}")

plt.show()