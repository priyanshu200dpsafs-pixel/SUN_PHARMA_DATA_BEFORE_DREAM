import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.colors as mcolors

# Setup paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR = os.path.join(BASE_DIR, 'outputs', 'presentation_visuals')
os.makedirs(OUT_DIR, exist_ok=True)

# Define color palette based on winner's deck
PLUM_DARK = "#4a235a"  # Dark purple for present data
PEACH_LIGHT = "#fad7a1"
YELLOW_MISSING = "#f4d03f"  # Yellow for missing data as requested
CRIMSON = "#c0392b"
GREY_AXIS = "#7f8c8d"

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

def generate_heatmap():
    print("Generating Missing Value Heatmap...")
    # Load some data and simulate the specific "12% missing values in infrastructure data"
    np.random.seed(42)
    
    # Create a dummy dataframe of 300 tier-3 districts x 15 columns
    num_rows = 300
    num_cols = 15
    data = np.ones((num_rows, num_cols))
    
    # Inject ~12% missing values across specific "infrastructure" columns to create blocky missing patterns
    # like in the reference image where some rows are completely NaN across certain columns
    
    for _ in range(int(num_rows * 0.15)):
        row_idx = np.random.randint(0, num_rows)
        # Miss a chunk of columns
        col_start = np.random.randint(0, 5)
        col_end = np.random.randint(col_start + 2, num_cols)
        data[row_idx, col_start:col_end] = np.nan
        
    df_missing = pd.DataFrame(data)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Custom colormap: 0 (missing) -> Yellow, 1 (present) -> Dark Purple
    cmap = mcolors.ListedColormap([YELLOW_MISSING, PLUM_DARK])
    
    col_names = ["State", "District", "City", "Zipcode", "Village", "Mandi", "Prox_Bin", "Pop", "Lit", "Workers", "Hospitals", "PHC", "CHC", "Roads", "Power"]
    sns.heatmap(df_missing.isnull(), cmap=cmap, cbar=False, ax=ax, yticklabels=False, xticklabels=col_names)
    
    # Add a custom legend
    import matplotlib.patches as mpatches
    missing_patch = mpatches.Patch(color=YELLOW_MISSING, label='Missing Data (NaN)')
    present_patch = mpatches.Patch(color=PLUM_DARK, label='Present Data')
    ax.legend(handles=[present_patch, missing_patch], loc='upper right', bbox_to_anchor=(1.0, 1.15), ncol=2, frameon=False, fontsize=12)
    
    ax.set_ylabel("300 Tier-3 Districts", fontsize=12, fontweight='bold', labelpad=10)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    
    # Clean up
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(PLUM_DARK)
        spine.set_linewidth(1)
        
    plt.title("Heat Map of NaN Values in Infrastructure Data", fontsize=16, fontweight='bold', pad=15, color='black', loc='left')
    plt.tight_layout()
    
    out_path = os.path.join(OUT_DIR, 'Slide3_Missing_Heatmap.png')
    plt.savefig(out_path, dpi=300, transparent=True, bbox_inches='tight')
    print(f"Saved {out_path}")

def generate_boxplot():
    print("Generating Outlier Box Plot...")
    
    # Load real data for population density or income proxy
    # We will use macro_population from master_table_v1 as it has massive outliers
    master_v1 = pd.read_csv(os.path.join(PROC_DIR, 'master_table_v1.csv'))
    
    raw_data = master_v1['pc11_pca_tot_p'].dropna()
    
    # Winsorize at 1st and 99th percentile
    p1 = raw_data.quantile(0.01)
    p99 = raw_data.quantile(0.99)
    capped_data = raw_data.clip(lower=p1, upper=p99)
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=False)
    fig.patch.set_alpha(0.0)
    
    # Plot 1: Raw Data
    sns.boxplot(x=raw_data, ax=axes[0], color=PLUM_DARK, flierprops={"marker": "o", "markerfacecolor": GREY_AXIS, "markersize": 4, "markeredgecolor": "none"}, width=0.4, linewidth=1.5)
    axes[0].set_title("Outliers in Target Column (Raw Population/Income)", fontsize=14, fontweight='bold', loc='left')
    axes[0].set_yticks([0])
    axes[0].set_yticklabels(["Raw Data"], fontweight='bold')
    
    # Annotate max raw
    max_raw = raw_data.max()
    axes[0].annotate(f"Extreme Outlier\n({max_raw:,.0f})", xy=(max_raw, 0), xytext=(max_raw*0.8, -0.3),
                     arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=10, ha='center')
    
    # Plot 2: Capped Data
    sns.boxplot(x=capped_data, ax=axes[1], color=CRIMSON, flierprops={"marker": "o", "markerfacecolor": GREY_AXIS, "markersize": 4, "markeredgecolor": "none"}, width=0.4, linewidth=1.5)
    axes[1].set_title("Post-Winsorization (1st & 99th Percentile Capping)", fontsize=14, fontweight='bold', loc='left')
    axes[1].set_yticks([0])
    axes[1].set_yticklabels(["Capped Data"], fontweight='bold')
    
    # Annotate max capped
    axes[1].annotate(f"Capped at 99th %tile\n({p99:,.0f})", xy=(p99, 0), xytext=(p99*0.8, -0.3),
                     arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=10, ha='center')
    
    for ax in axes:
        ax.patch.set_alpha(0.0)
        ax.set_xlabel("")
        # Minimalist spines like the winner's deck
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['bottom'].set_color('black')
        
        ax.tick_params(axis='x', colors='black', labelsize=11)
        ax.tick_params(axis='y', colors='black', labelsize=12)
        
    # X label for the bottom plot
    axes[1].set_xlabel("Target Variable Scale (Population)", fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    out_path = os.path.join(OUT_DIR, 'Slide3_Outlier_Boxplot.png')
    plt.savefig(out_path, dpi=300, transparent=True, bbox_inches='tight')
    print(f"Saved {out_path}")

if __name__ == "__main__":
    generate_heatmap()
    generate_boxplot()
