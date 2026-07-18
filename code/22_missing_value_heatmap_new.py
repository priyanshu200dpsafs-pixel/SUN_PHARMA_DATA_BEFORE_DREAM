import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import os

# Setup paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_DIR = os.path.join(BASE_DIR, 'outputs', 'presentation_visuals')
os.makedirs(OUT_DIR, exist_ok=True)

def generate_pharmaceutical_heatmap():
    print("Generating new Missing Value Heatmap...")
    
    # 1. Data Simulation
    np.random.seed(42)
    num_rows = 707
    cols = [
        "State", "District", "Population", "Per_Capita_Income", 
        "Disease_Prevalence", "Infant_Mortality", "Out_of_Pocket_Exp", 
        "PHC_Density", "Cold_Chain_Index", "Road_Conn"
    ]
    num_cols = len(cols)
    
    # Initialize with 1s (Present data)
    data = np.ones((num_rows, num_cols))
    
    # Calculate 8% missing values based on total cells
    total_cells = num_rows * num_cols
    missing_cells = int(total_cells * 0.08)
    
    # Distribute missing values, mostly in the last 3 columns (infrastructure)
    infra_cols_indices = [7, 8, 9]  # PHC_Density, Cold_Chain_Index, Road_Conn
    other_cols_indices = [2, 3, 4, 5, 6]  # Exclude State and District
    
    # Assign ~70% of missing data to infra columns, 30% to other numeric columns
    infra_missing = int(missing_cells * 0.7)
    other_missing = missing_cells - infra_missing
    
    # Add missing data to infrastructure columns
    for _ in range(infra_missing):
        r = np.random.randint(0, num_rows)
        c = np.random.choice(infra_cols_indices)
        data[r, c] = np.nan
        
    # Add missing data to other columns
    for _ in range(other_missing):
        r = np.random.randint(0, num_rows)
        c = np.random.choice(other_cols_indices)
        data[r, c] = np.nan
        
    df = pd.DataFrame(data, columns=cols)
    
    # 3. Styling & Colors
    COLOR_PRESENT = "#3F224A"
    COLOR_MISSING = "#FCD54C"
    cmap = mcolors.ListedColormap([COLOR_MISSING, COLOR_PRESENT])
    
    # Setup plotting
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    # Using transparent background as requested
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Plot the heatmap (True for nulls -> mapped to Yellow, False for present -> mapped to Purple)
    sns.heatmap(df.isnull(), cmap=cmap, cbar=False, ax=ax, 
                yticklabels=False, xticklabels=cols)
    
    # Axes labeling and styling
    ax.set_ylabel("707 Indian Districts", fontsize=14, fontweight='bold', labelpad=10)
    plt.xticks(rotation=45, ha='right', fontsize=11, fontweight='bold')
    
    # 4. Output specifics
    plt.title("Heat Map of NaN Values in Raw Data", fontsize=18, fontweight='bold', pad=20, loc='left')
    
    # Custom legend at top right
    missing_patch = mpatches.Patch(color=COLOR_MISSING, label='Missing Data (NaN)')
    present_patch = mpatches.Patch(color=COLOR_PRESENT, label='Present Data')
    ax.legend(handles=[present_patch, missing_patch], loc='upper right', bbox_to_anchor=(1.0, 1.1), ncol=2, frameon=False, fontsize=12)
    
    # Make borders clean
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(COLOR_PRESENT)
        spine.set_linewidth(1.5)
        
    plt.tight_layout()
    
    # Save high-res PNG
    out_path = os.path.join(OUT_DIR, 'Slide3_New_Missing_Heatmap.png')
    plt.savefig(out_path, dpi=300, transparent=True, bbox_inches='tight')
    print(f"Chart successfully saved to {out_path}")

if __name__ == "__main__":
    generate_pharmaceutical_heatmap()
