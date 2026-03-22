import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import os

# Automatically detect folder and set save path
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'gold_campaign_timeline_accurate.png')

# Exact anchor points from your transaction logs
# Format: Day of Simulation (Approx), Actual GC Price Traded
timeline_days = np.array([0,   6,    7,    12,   24,   31,   48,   49,   55])
actual_prices = np.array([5300, 5345, 5462, 5400, 5420, 5430, 5385, 5415, 5405])

# Create a smooth curve through your exact traded prices
spline = make_interp_spline(timeline_days, actual_prices, k=3)
smooth_days = np.linspace(timeline_days.min(), timeline_days.max(), 500)
smooth_prices = spline(smooth_days)

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(smooth_days, smooth_prices, color='goldenrod', linewidth=3, label='Actual GC Price Trend')

# Plot your actual transaction points on the curve
ax.scatter(timeline_days[1:8], actual_prices[1:8], color='black', zorder=5, label='Your Executions')

# Highlight Phase 1: Rangebound Premium Collection (Jan 30 - Feb 6)
ax.axvspan(0, 10, color='gray', alpha=0.1)
ax.annotate('Phase 1: Volatility Starts\n(GLD Strangle & Short Calls)', xy=(5, 5250), ha='center', fontsize=10, fontweight='bold')

# Highlight Phase 2: The Breakout (Feb 11 - Feb 23)
ax.axvspan(10, 28, color='green', alpha=0.1)
ax.annotate('Phase 2: Aggressive Longs\n(+ $18,700 on 5150 Calls)', xy=(19, 5480), ha='center', fontsize=10, fontweight='bold', color='darkgreen')

# Highlight Phase 3: The Peak-IV Trap (March 2 - March 15)
ax.axvspan(28, 42, color='red', alpha=0.1)
ax.annotate('Phase 3: The Chop / IV Trap\n(IV Crush on 5400 Calls)', xy=(35, 5450), ha='center', fontsize=10, fontweight='bold', color='darkred')

# Highlight Phase 4: Recovery & Discipline (March 16+)
ax.axvspan(42, 55, color='blue', alpha=0.1)
ax.annotate('Phase 4: Tactical Recovery\n(Bought 5385, Sold 5415)', xy=(48, 5330), ha='center', fontsize=10, fontweight='bold', color='darkblue')

# Formatting
ax.set_title('The Gold Campaign: Actual Execution Timeline (Audited Prices)', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Simulation Timeline (Late Jan - Late Mar)', fontsize=12, fontweight='bold')
ax.set_ylabel('Actual Gold (GC) Price Level ($)', fontsize=12, fontweight='bold')
ax.set_xticks([]) # Hide arbitrary date numbers for a cleaner look
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(loc='lower left')

# Clean borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save and show
plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Success! Accurate Gold timeline chart saved to: {output_path}")
plt.show()