import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import os

# 1. Data Simulation
rows = 707
columns = [
    'State', 'District', 'Population', 'Per_Capita_Income', 'Disease_Prevalence', 
    'Infant_Mortality', 'Out_of_Pocket_Exp', 'PHC_Density', 'Cold_Chain_Index', 'Road_Conn'
]

# Generate random data
# We can use any dummy data since we only care about the NaN mask
data = np.random.rand(rows, len(columns))

# Introduce 8% missing values
total_cells = rows * len(columns)
missing_cells_count = int(round(total_cells * 0.08))

# Get random 1D indices and convert to 2D indices
missing_indices_1d = np.random.choice(total_cells, missing_cells_count, replace=False)
missing_indices_2d = np.unravel_index(missing_indices_1d, (rows, len(columns)))

# Set missing values
data[missing_indices_2d] = np.nan

df = pd.DataFrame(data, columns=columns)

# 2. Plot Setup
# Set seaborn style for clean axes (optional, but looks good)
sns.set_theme(style="white")

plt.figure(figsize=(14, 8))

# Color Mapping:
# Present (92%): #0F2046 (Deep Navy Blue) - maps to 0 / False in df.isnull()
# Missing (8%): #F37021 (Sun Pharma Orange) - maps to 1 / True in df.isnull()
cmap = mcolors.ListedColormap(['#0F2046', '#F37021'])

# Create Heatmap
ax = sns.heatmap(df.isnull(), cmap=cmap, cbar=False, yticklabels=False)

# Formatting the X-axis for better readability
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=11)

# Title
plt.title('Heat Map of NaN Values in Raw Data', fontsize=18, pad=20)

# Clean legend at the top right
present_patch = mpatches.Patch(color='#0F2046', label='Present Data')
missing_patch = mpatches.Patch(color='#F37021', label='Missing Data (NaN)')

# Add legend at the top right (inside or slightly outside the plot area as needed)
# Using bbox_to_anchor to place it nicely at the top right
plt.legend(handles=[present_patch, missing_patch], loc='upper right', bbox_to_anchor=(1.25, 1.0), frameon=True, fontsize=12, title='Legend', title_fontsize=14)

plt.tight_layout()

# Save Output
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'outputs', 'visuals')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'Missing_Value_Heatmap.png')

plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Heatmap saved to {output_path}")
