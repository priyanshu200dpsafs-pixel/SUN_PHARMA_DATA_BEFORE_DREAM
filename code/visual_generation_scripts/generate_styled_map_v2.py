import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import os
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe

def create_styled_map():
    shape_path = "/Users/priyanshu/Desktop/Sun_Pharma_Project/raw_data/01_geography/district.gpkg"
    gdf = gpd.read_file(shape_path)
    
    # We will simulate multiple points to represent the 3 clusters
    np.random.seed(42)
    
    # Cluster 1 (South/West) - Deep Plum, Large
    tier1_lon = np.concatenate([np.random.normal(73.5, 0.4, 15), 
                                np.random.normal(77.5, 0.5, 15),
                                np.random.normal(80.2, 0.4, 10),
                                np.random.normal(76.5, 0.6, 10)])
    tier1_lat = np.concatenate([np.random.normal(18.5, 0.4, 15), 
                                np.random.normal(12.9, 0.5, 15),
                                np.random.normal(13.0, 0.4, 10),
                                np.random.normal(10.0, 0.6, 10)])
    
    # Cluster 2 (Inland) - Crimson Red, Medium
    tier2_lon = np.concatenate([np.random.normal(72.5, 0.6, 12), 
                                np.random.normal(78.4, 0.6, 12),
                                np.random.normal(73.8, 0.5, 8),
                                np.random.normal(76.9, 0.5, 8)])
    tier2_lat = np.concatenate([np.random.normal(23.0, 0.6, 12), 
                                np.random.normal(17.3, 0.6, 12),
                                np.random.normal(20.0, 0.5, 8),
                                np.random.normal(11.0, 0.5, 8)])
    
    # Cluster 3 (North) - Warm Peach, Small
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
    
    # Plot Base Map: Solid Slate Blue (#D9E2EC) with pure White (#FFFFFF) borders, line width 1.5
    gdf.plot(ax=ax, color='#D9E2EC', edgecolor='#FFFFFF', linewidth=1.5)
    
    # Path effects for drop shadow on scatter bubbles
    shadow = [pe.SimplePatchShadow(offset=(1.5, -1.5), shadow_rgbFace='black', alpha=0.3), pe.Normal()]
    
    # Plot Cluster 3 (Warm Peach)
    ax.scatter(tier3_lon, tier3_lat, s=50, color='#F5CBA7', alpha=0.9, edgecolor='white', linewidth=0.5, zorder=5, path_effects=shadow)
    # Plot Cluster 2 (Crimson Red)
    ax.scatter(tier2_lon, tier2_lat, s=150, color='#C0392B', alpha=0.9, edgecolor='white', linewidth=0.8, zorder=6, path_effects=shadow)
    # Plot Cluster 1 (Deep Plum)
    ax.scatter(tier1_lon, tier1_lat, s=350, color='#4A235A', alpha=0.9, edgecolor='white', linewidth=1.0, zorder=7, path_effects=shadow)
    
    ax.axis('off')
    
    # Add a continuous colorbar/legend matching the 3 clusters
    cmap = mcolors.LinearSegmentedColormap.from_list("cluster_cmap", ["#F5CBA7", "#C0392B", "#4A235A"])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=100))
    sm.set_array([])
    
    cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.04)
    cbar.set_label('Cluster Viability', rotation=270, labelpad=20, fontweight='bold', color='#4A235A')
    
    cbar.set_ticks([5, 50, 95])
    cbar.set_ticklabels(['Cluster 3\n(Low)', 'Cluster 2\n(Med)', 'Cluster 1\n(High)'])
    cbar.ax.tick_params(colors='#2D2D2D', labelsize=9, length=0)
    cbar.outline.set_visible(False)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'Styled_Cluster_Map.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Map saved to {output_path}")

if __name__ == "__main__":
    create_styled_map()
