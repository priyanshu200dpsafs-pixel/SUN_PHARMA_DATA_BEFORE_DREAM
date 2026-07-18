import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

def create_correlation_heatmap():
    # 1. Define Features
    features = [
        "Per_Capita_Income",
        "Urbanization_Rate",
        "Chronic_Disease_Rate",
        "Out_of_Pocket_Exp",
        "Cold_Chain_Index",
        "Road_Density",
        "Hospital_Beds"
    ]
    
    n = len(features)
    
    # 2. Simulate Correlation Matrix
    np.random.seed(42)
    # Generate random moderate to low correlations (-0.3 to 0.6)
    matrix = np.random.uniform(-0.3, 0.6, size=(n, n))
    
    # Make it symmetric
    matrix = (matrix + matrix.T) / 2
    
    # Set diagonal to 1.0
    np.fill_diagonal(matrix, 1.0)
    
    # Find indices for specific rule
    urb_idx = features.index("Urbanization_Rate")
    hosp_idx = features.index("Hospital_Beds")
    
    # Apply rule: Hospital_Beds and Urbanization_Rate highly correlated
    matrix[urb_idx, hosp_idx] = 0.92
    matrix[hosp_idx, urb_idx] = 0.92
    
    # Create DataFrame for Seaborn
    corr = pd.DataFrame(matrix, index=features, columns=features)
    
    # 3. Styling
    # Sun Pharma Orange (High Negative) -> White (Zero) -> Navy Blue (High Positive)
    colors = ["#F37021", "#FFFFFF", "#0F2046"]
    cmap = LinearSegmentedColormap.from_list("sun_pharma_corr", colors)
    
    # Create lower-triangle mask
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    # Set up the matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Set figure and axis background to transparent
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Draw the heatmap
    sns.heatmap(
        corr, 
        mask=mask, 
        cmap=cmap, 
        annot=True,     # Annotate with actual decimal numbers
        fmt=".2f",      # 2 decimal places
        vmin=-1, vmax=1,# Range -1 to 1 for correlation
        center=0,       # Center at 0 (White)
        square=True,    # Square cells
        linewidths=0.5, # Small gaps between cells
        cbar_kws={"shrink": .75, "label": "Correlation Coefficient"}
    )
    
    # Title formatting
    plt.title("Feature Correlation Matrix", fontsize=16, pad=20)
    
    # Fix layout
    plt.tight_layout()
    
    # 4. Output
    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Project/outputs/visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Feature_Correlation_Matrix.png')
    
    # Save as high-resolution (300 DPI) PNG with transparent background
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    print(f"Correlation heatmap saved to {output_path}")

if __name__ == "__main__":
    create_correlation_heatmap()
