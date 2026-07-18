import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import os

def create_bubble_map():
    # Load India map
    shape_path = "/Users/priyanshu/Desktop/Sun_Pharma_Project/raw_data/01_geography/district.gpkg"
    gdf = gpd.read_file(shape_path)
    
    # Dissolve to get just the outer boundary for an ultra-minimalist look
    india_outline = gdf.dissolve()
    
    # City Coordinates (Lon, Lat)
    cities = [
        # Tier 1
        {"name": "Pune", "lon": 73.8567, "lat": 18.5204, "tier": "Tier 1"},
        {"name": "Mumbai", "lon": 72.8777, "lat": 19.0760, "tier": "Tier 1"},
        {"name": "Bengaluru", "lon": 77.5946, "lat": 12.9716, "tier": "Tier 1"},
        {"name": "Chennai", "lon": 80.2707, "lat": 13.0827, "tier": "Tier 1"},
        {"name": "Ernakulam", "lon": 76.2999, "lat": 9.9816, "tier": "Tier 1"},
        # Tier 2
        {"name": "Ahmedabad", "lon": 72.5714, "lat": 23.0225, "tier": "Tier 2"},
        {"name": "Hyderabad", "lon": 78.4867, "lat": 17.3850, "tier": "Tier 2"},
        {"name": "Coimbatore", "lon": 76.9558, "lat": 11.0168, "tier": "Tier 2"},
        {"name": "Nashik", "lon": 73.7898, "lat": 19.9975, "tier": "Tier 2"},
        # Tier 3
        {"name": "Patna", "lon": 85.1376, "lat": 25.5941, "tier": "Tier 3"},
        {"name": "Lucknow", "lon": 80.9462, "lat": 26.8467, "tier": "Tier 3"},
        {"name": "Jaipur", "lon": 75.7873, "lat": 26.9124, "tier": "Tier 3"},
        {"name": "Bhopal", "lon": 77.4126, "lat": 23.2599, "tier": "Tier 3"}
    ]
    
    df = pd.DataFrame(cities)
    
    fig, ax = plt.subplots(figsize=(5, 6))
    
    # Transparent backgrounds
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
    
    # Plot Base Map (minimalist, ultra-light grey outline of India)
    india_outline.plot(ax=ax, color='#F8F9FA', edgecolor='#D3D3D3', linewidth=0.8)
    
    # Plot Tiers
    tier1 = df[df['tier'] == 'Tier 1']
    ax.scatter(tier1['lon'], tier1['lat'], s=150, color='#0F2046', 
               edgecolor='white', linewidth=1, label='Tier 1 (High Priority)', alpha=0.95, zorder=5)
               
    tier2 = df[df['tier'] == 'Tier 2']
    ax.scatter(tier2['lon'], tier2['lat'], s=75, color='#F37021', 
               edgecolor='white', linewidth=1, label='Tier 2 (Medium Priority)', alpha=0.95, zorder=4)
               
    tier3 = df[df['tier'] == 'Tier 3']
    ax.scatter(tier3['lon'], tier3['lat'], s=25, color='#B0B0B0', 
               edgecolor='white', linewidth=0.5, label='Tier 3 (Background)', alpha=0.8, zorder=3)
               
    # Add title at top left
    ax.set_title('National Hotspots: The Western & Southern Dominance', 
                 loc='left', color='#0F2046', fontsize=12, fontweight='bold', pad=10)
                 
    ax.axis('off') # Remove axis ticks and borders
    
    # Adjust Legend
    ax.legend(loc='lower right', frameon=False, fontsize=9)
    
    output_dir = '/Users/priyanshu/Desktop'
    output_path = os.path.join(output_dir, 'National_Hotspots_BubbleMap.png')
    
    plt.savefig(output_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Bubble map saved to {output_path}")

if __name__ == "__main__":
    create_bubble_map()
