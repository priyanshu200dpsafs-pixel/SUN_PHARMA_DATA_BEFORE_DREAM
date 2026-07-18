import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import os
import matplotlib.colors as mcolors

def create_density_map():
    shape_path = "/Users/priyanshu/Desktop/Sun_Pharma_Project/raw_data/01_geography/district.gpkg"
    gdf = gpd.read_file(shape_path)
    
    # Dissolve to get a minimalist light grey map outline as requested
    india_outline = gdf.dissolve()
    
    # We will simulate multiple points to represent "MAI density" clusters
    np.random.seed(42)
    
    # Tier 1 (South/West) - High density, Large Navy bubbles
    # Clusters around Mumbai/Pune, Bangalore, Chennai, Kerala
    tier1_lon = np.concatenate([np.random.normal(73.5, 0.4, 15), 
                                np.random.normal(77.5, 0.5, 15),
                                np.random.normal(80.2, 0.4, 10),
                                np.random.normal(76.5, 0.6, 10)])
    tier1_lat = np.concatenate([np.random.normal(18.5, 0.4, 15), 
                                np.random.normal(12.9, 0.5, 15),
                                np.random.normal(13.0, 0.4, 10),
                                np.random.normal(10.0, 0.6, 10)])
    
    # Tier 2 (Inland) - Medium density, Medium Teal bubbles
    # Clusters around Ahmedabad, Hyderabad, Nashik, Coimbatore
    tier2_lon = np.concatenate([np.random.normal(72.5, 0.6, 12), 
                                np.random.normal(78.4, 0.6, 12),
                                np.random.normal(73.8, 0.5, 8),
                                np.random.normal(76.9, 0.5, 8)])
    tier2_lat = np.concatenate([np.random.normal(23.0, 0.6, 12), 
                                np.random.normal(17.3, 0.6, 12),
                                np.random.normal(20.0, 0.5, 8),
                                np.random.normal(11.0, 0.5, 8)])
    
    # Tier 3 (North) - Low density, Small Orange dots
    # Clusters around Patna, Lucknow, Jaipur
    tier3_lon = np.concatenate([np.random.normal(85.1, 0.8, 20), 
                                np.random.normal(80.9, 0.8, 20), 
                                np.random.normal(75.7, 0.8, 20)])
    tier3_lat = np.concatenate([np.random.normal(25.5, 0.8, 20), 
                                np.random.normal(26.8, 0.8, 20), 
                                np.random.normal(26.9, 0.8, 20)])
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Plot Drop Shadow
    # Translate the geometry slightly (approx 15-20km offset) to create a shadow effect
    india_shadow = india_outline.translate(xoff=0.2, yoff=-0.2)
    india_shadow.plot(ax=ax, color='#2F4F4F', edgecolor='none', alpha=0.3)
    
    # Plot Base Map with Bold Deep Navy Outline
    india_outline.plot(ax=ax, color='#F8F9FA', edgecolor='#0F2046', linewidth=1.5)
    
    # Plot Density Scatters (Semi-transparent)
    # Tier 3
    ax.scatter(tier3_lon, tier3_lat, s=30, color='#F37021', alpha=0.5, edgecolor='none')
    # Tier 2
    ax.scatter(tier2_lon, tier2_lat, s=120, color='#00A8B5', alpha=0.6, edgecolor='none')
    # Tier 1
    ax.scatter(tier1_lon, tier1_lat, s=300, color='#0F2046', alpha=0.7, edgecolor='none')
    
    ax.axis('off')
    
    # Add a continuous colorbar/legend
    # Define a custom colormap that transitions from Orange -> Teal -> Navy
    cmap = mcolors.LinearSegmentedColormap.from_list("mai_cmap", ["#F37021", "#00A8B5", "#0F2046"])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=100))
    sm.set_array([])
    
    cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.04)
    cbar.set_label('MAI Score (Predicted)', rotation=270, labelpad=20, fontweight='bold', color='#0F2046')
    
    # Set discrete ticks representing the tiers
    cbar.set_ticks([5, 50, 95])
    cbar.set_ticklabels(['Tier 3\n(Low)', 'Tier 2\n(Med)', 'Tier 1\n(High)'])
    cbar.ax.tick_params(colors='#2D2D2D', labelsize=9, length=0) # hide tick marks, keep text
    cbar.outline.set_visible(False)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'MAI_Density_Map.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Map saved to {output_path}")

if __name__ == "__main__":
    create_density_map()
