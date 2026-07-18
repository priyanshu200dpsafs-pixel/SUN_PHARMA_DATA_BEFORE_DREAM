import matplotlib.pyplot as plt
import matplotlib.path as mpath
import geopandas as gpd
import pandas as pd
import os

def get_pin_marker():
    # Define a teardrop/Google-pin like SVG path
    path_data = [
        (mpath.Path.MOVETO, (0.0, 0.0)),
        (mpath.Path.CURVE4, (0.8, 0.8)),
        (mpath.Path.CURVE4, (1.0, 1.8)),
        (mpath.Path.CURVE4, (0.0, 2.6)),
        (mpath.Path.CURVE4, (-1.0, 1.8)),
        (mpath.Path.CURVE4, (-0.8, 0.8)),
        (mpath.Path.CLOSEPOLY, (0.0, 0.0))
    ]
    codes, verts = zip(*path_data)
    return mpath.Path(verts, codes)

def create_bubble_map_v4():
    shape_path = "/Users/priyanshu/Desktop/Sun_Pharma_Project/raw_data/01_geography/district.gpkg"
    gdf = gpd.read_file(shape_path)
    india_outline = gdf.dissolve()
    
    cities = [
        {"name": "Pune", "lon": 73.8567, "lat": 18.5204, "tier": "Tier 1"},
        {"name": "Mumbai", "lon": 72.8777, "lat": 19.0760, "tier": "Tier 1"},
        {"name": "Bengaluru", "lon": 77.5946, "lat": 12.9716, "tier": "Tier 1"},
        {"name": "Chennai", "lon": 80.2707, "lat": 13.0827, "tier": "Tier 1"},
        {"name": "Ernakulam", "lon": 76.2999, "lat": 9.9816, "tier": "Tier 1"},
        {"name": "Ahmedabad", "lon": 72.5714, "lat": 23.0225, "tier": "Tier 2"},
        {"name": "Hyderabad", "lon": 78.4867, "lat": 17.3850, "tier": "Tier 2"},
        {"name": "Coimbatore", "lon": 76.9558, "lat": 11.0168, "tier": "Tier 2"},
        {"name": "Nashik", "lon": 73.7898, "lat": 19.9975, "tier": "Tier 2"},
        {"name": "Patna", "lon": 85.1376, "lat": 25.5941, "tier": "Tier 3"},
        {"name": "Lucknow", "lon": 80.9462, "lat": 26.8467, "tier": "Tier 3"},
        {"name": "Jaipur", "lon": 75.7873, "lat": 26.9124, "tier": "Tier 3"}
    ]
    df = pd.DataFrame(cities)
    
    # Custom Offsets to prevent overlap (x_offset, y_offset, horizontal_alignment)
    offsets = {
        "Mumbai": (-0.6, 0.2, 'right'),
        "Pune": (0.6, -0.4, 'left'),
        "Bengaluru": (-0.6, -0.2, 'right'),
        "Chennai": (0.6, 0.2, 'left'),
        "Nashik": (0.6, 0.2, 'left'),
        "Ahmedabad": (0.6, -0.2, 'left'),
        "Coimbatore": (0.6, -0.2, 'left'),
        "Ernakulam": (0.6, 0.0, 'left'),
        "Hyderabad": (0.6, 0.0, 'left'),
        "Patna": (0.5, 0.0, 'left'),
        "Lucknow": (0.5, 0.0, 'left'),
        "Jaipur": (0.5, 0.0, 'left')
    }
    
    fig, ax = plt.subplots(figsize=(4, 5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    india_outline.plot(ax=ax, color='#F8F9FA', edgecolor='#D3D3D3', linewidth=0.8)
    
    pin = get_pin_marker()
    
    def plot_tier(tier_name, color, size, label, fontsize):
        tier_data = df[df['tier'] == tier_name]
        
        # Plot the main Google pin shape
        ax.scatter(tier_data['lon'], tier_data['lat'], s=size, marker=pin, color=color, 
                   edgecolor='white', linewidth=0.5, label=label, alpha=0.95, zorder=5)
                   
        # Add the inner white circle to complete the Google Pin look
        # We shift slightly up (lat + 0.35) so it sits exactly in the "head" of the pin
        ax.scatter(tier_data['lon'], tier_data['lat'] + 0.35, s=size*0.15, marker='o', 
                   color='white', zorder=6)
        
        for idx, row in tier_data.iterrows():
            city = row['name']
            off_x, off_y, align = offsets.get(city, (0.6, 0, 'left'))
            
            # Shift the text up slightly to align with the pin head visually
            ax.text(row['lon'] + off_x, row['lat'] + off_y + 0.35, city, 
                    fontsize=fontsize, fontweight='bold', color=color, 
                    va='center', ha=align, zorder=7)

    # Plot Tiers
    plot_tier('Tier 1', '#0F2046', 300, 'Tier 1 (High Priority)', 7)
    plot_tier('Tier 2', '#F37021', 200, 'Tier 2 (Medium Priority)', 6)
    plot_tier('Tier 3', '#B0B0B0', 100, 'Tier 3 (Background)', 5)
    
    ax.set_title('MAI Hotspots: Western & Southern Dominance', 
                 loc='left', color='#0F2046', fontsize=10, fontweight='bold', pad=10)
                 
    ax.axis('off')
    
    # Custom legend to show pins correctly
    ax.legend(loc='lower right', frameon=False, fontsize=7)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'MAI_Hotspots_GooglePins.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Map saved to {output_path}")

if __name__ == "__main__":
    create_bubble_map_v4()
