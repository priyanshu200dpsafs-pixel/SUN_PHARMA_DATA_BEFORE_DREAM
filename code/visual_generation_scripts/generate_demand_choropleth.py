import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os

def create_choropleth():
    # 1. Load Data
    gpkg_path = '/Users/priyanshu/Desktop/Sun_Pharma_Project/raw_data/01_geography/district.gpkg'
    gdf = gpd.read_file(gpkg_path)

    # 2. Simulate 'Latent Healthcare Demand Index'
    # Base random demand (30 - 70) for all districts
    np.random.seed(42) # For reproducibility
    gdf['Latent_Healthcare_Demand'] = np.random.uniform(30, 70, len(gdf))

    # High Demand States (UP: '09', Bihar: '10', MP: '23', Rajasthan: '08')
    high_demand_states = ['08', '09', '10', '23']
    high_mask = gdf['pc11_state_id'].isin(high_demand_states)
    gdf.loc[high_mask, 'Latent_Healthcare_Demand'] = np.random.uniform(75, 100, high_mask.sum())

    # Low Demand States (Gujarat: '24', Maharashtra: '27', Kerala: '32', TN: '33')
    low_demand_states = ['24', '27', '32', '33']
    low_mask = gdf['pc11_state_id'].isin(low_demand_states)
    gdf.loc[low_mask, 'Latent_Healthcare_Demand'] = np.random.uniform(0, 25, low_mask.sum())

    # Ensure values are strictly between 0 and 100
    gdf['Latent_Healthcare_Demand'] = gdf['Latent_Healthcare_Demand'].clip(0, 100)

    # 3. Styling & Colors
    # Sequential color gradient: Light Peach/Yellow -> Sun Pharma Orange -> Dark Red/Crimson
    # No Green.
    colors = ['#FDE0BA', '#F37021', '#8B0000'] 
    n_bins = 100  # Discretizes the interpolation into bins
    cmap_name = 'custom_demand'
    custom_cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

    # 4. Plotting
    fig, ax = plt.subplots(1, 1, figsize=(10, 12))
    
    # Remove all axis grids, lat/long lines, and background colors
    ax.axis('off')
    fig.patch.set_alpha(0.0) # Transparent figure background
    ax.patch.set_alpha(0.0)  # Transparent axes background

    # Plot the choropleth
    gdf.plot(
        column='Latent_Healthcare_Demand',
        cmap=custom_cmap,
        linewidth=0.1,
        edgecolor='black', # very thin border for districts
        ax=ax,
        vmin=0, vmax=100
    )

    # 5. Color Scale Legend
    # Create colorbar
    sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=plt.Normalize(vmin=0, vmax=100))
    sm._A = [] # fake up the array of the scalar mappable
    
    # Add colorbar to figure
    cbar = fig.colorbar(sm, ax=ax, shrink=0.5, aspect=20, orientation='vertical', pad=0.02)
    cbar.set_label('Latent Healthcare Demand Index (0-100)', fontsize=12, labelpad=15)
    cbar.ax.tick_params(labelsize=10)
    
    # cbar.patch.set_alpha(0.0)

    # 6. Output
    output_dir = '/Users/priyanshu/Desktop/Sun_Pharma_Visuals'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Latent_Demand_Choropleth.png')
    
    # Save as high-resolution (300 DPI) PNG with transparent background
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    print(f"Choropleth map saved to {output_path}")

if __name__ == "__main__":
    create_choropleth()
