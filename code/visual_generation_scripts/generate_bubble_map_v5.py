import matplotlib.pyplot as plt
import matplotlib.path as mpath
import geopandas as gpd
import pandas as pd
import os
import textwrap

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

def create_bubble_map_v5():
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
    
    # Increase height to make space for explanation text at the bottom
    fig, ax = plt.subplots(figsize=(4, 6.5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Plot districts with darker boundaries for visibility on white backgrounds
    gdf.plot(ax=ax, color='#F8F9FA', edgecolor='#A0A0A0', linewidth=0.5)
    
    pin = get_pin_marker()
    
    def plot_tier(tier_name, color, size, label, fontsize, text_color=None):
        if text_color is None:
            text_color = color
            
        tier_data = df[df['tier'] == tier_name]
        
        # Plot the main Google pin shape
        ax.scatter(tier_data['lon'], tier_data['lat'], s=size, marker=pin, color=color, 
                   edgecolor='white', linewidth=0.5, label=label, alpha=0.95, zorder=5)
                   
        # Add the inner white circle
        ax.scatter(tier_data['lon'], tier_data['lat'] + 0.35, s=size*0.15, marker='o', 
                   color='white', zorder=6)
        
        for idx, row in tier_data.iterrows():
            city = row['name']
            off_x, off_y, align = offsets.get(city, (0.6, 0, 'left'))
            
            ax.text(row['lon'] + off_x, row['lat'] + off_y + 0.35, city, 
                    fontsize=fontsize, fontweight='bold', color=text_color, 
                    va='center', ha=align, zorder=7)

    # Tier 1: Orange (matches text description)
    plot_tier('Tier 1', '#F37021', 300, 'Tier 1 (High Priority)', 7)
    # Tier 2: Deep Navy
    plot_tier('Tier 2', '#0F2046', 200, 'Tier 2 (Medium Priority)', 6)
    # Tier 3: Darker Grey (so it's visible on white)
    plot_tier('Tier 3', '#707070', 100, 'Tier 3 (Background)', 6, text_color='#505050')
    
    ax.set_title('MAI Hotspots: Western & Southern Dominance', 
                 loc='left', color='#0F2046', fontsize=10, fontweight='bold', pad=10)
                 
    ax.axis('off')
    
    ax.legend(loc='lower right', frameon=False, fontsize=7)
    
    # Shrink the map area slightly to leave physical room at the bottom for text
    plt.subplots_adjust(bottom=0.25)
    
    # Add explanation text
    explanation_title = "Geospatial Distribution of Predicted Viability"
    explanation_body = (
        "As illustrated in the map, regions with higher predicted market attractiveness (indicated by the larger orange nodes) "
        "strongly overlap with Western and Southern infrastructure corridors. While Northern regions possess high raw population "
        "density, our model heavily penalizes these districts due to sparse cold-chain logistics and lower baseline affordability. "
        "This validates the strategy of concentrating physical deployments in regions where wealth and infrastructure positively interact."
    )
    
    wrapped_body = "\n".join(textwrap.wrap(explanation_body, width=58))
    
    # Title of text block
    fig.text(0.05, 0.18, explanation_title, fontsize=8, fontweight='bold', color='#0F2046', ha='left')
    # Body of text block
    fig.text(0.05, 0.02, wrapped_body, fontsize=6.5, color='#2D2D2D', ha='left', va='bottom', linespacing=1.6)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'MAI_Hotspots_Explained.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Map with explanation saved to {output_path}")

if __name__ == "__main__":
    create_bubble_map_v5()
