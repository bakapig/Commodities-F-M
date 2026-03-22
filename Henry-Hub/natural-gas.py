import matplotlib.pyplot as plt
import os

# 1. Automatically detect the folder where this script is saved
script_dir = os.path.dirname(os.path.abspath(__file__))
# 2. Create the exact file path for the image next to the script
output_path = os.path.join(script_dir, 'natural_gas_seasonality.png')

# Define the data
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
index_values = [95, 90, 65, 55, 60, 70, 80, 85, 70, 65, 85, 95]

# Create the figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the main seasonality curve
ax.plot(months, index_values, marker='o', color='#1f77b4', linewidth=3, markersize=8, label='Demand/Price Index')

# Highlight the Spring Shoulder Season (March to May)
# In a 0-indexed list, Mar=2, Apr=3, May=4
ax.axvspan(2, 4, color='#ff7f0e', alpha=0.2, label='Spring Shoulder Season')

# Add an annotation for the drop
ax.annotate('Demand Collapse', 
            xy=(3, 55), 
            xytext=(4, 45),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=7),
            fontsize=12, fontweight='bold', ha='center')

# Formatting and Styling
ax.set_title('Historical Seasonality of Natural Gas (Henry Hub)', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Relative Demand / Price Index', fontsize=12, fontweight='bold')
ax.set_ylim(40, 105)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(loc='upper center', fontsize=11)

# Clean up top and right borders for a modern look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save the plot explicitly to the script's directory
plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# Print a confirmation message to the terminal so you know exactly where it went
print(f"Success! Chart saved to: {output_path}")

# Display the plot on your screen
plt.show()