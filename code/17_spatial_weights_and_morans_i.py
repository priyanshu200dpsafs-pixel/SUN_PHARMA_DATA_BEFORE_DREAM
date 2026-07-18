"""
17_spatial_weights_and_morans_i.py

Builds a spatial weights matrix (Queen contiguity) and computes Moran's I
for Overall MAI and Latent Demand Gap to assess spatial autocorrelation.
"""

import pandas as pd
import geopandas as gpd
import os
import libpysal
import esda
from splot.esda import plot_moran
import matplotlib.pyplot as plt

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR   = os.path.join(BASE_DIR, 'raw_data')
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')
VIS_DIR   = os.path.join(OUT_DIR, 'visuals')

os.makedirs(VIS_DIR, exist_ok=True)

def main():
    print("="*60)
    print("  SPATIAL AUTOCORRELATION ANALYSIS (MORAN'S I)")
    print("="*60)
    
    # ── 1. Load Data ──
    master = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))
    geography = pd.read_csv(os.path.join(PROC_DIR, 'geography_master.csv'))
    indices = pd.read_csv(os.path.join(OUT_DIR, 'final_indices.csv'))
    gap = pd.read_csv(os.path.join(OUT_DIR, 'latent_demand_gap_v2.csv'))
    
    # Merge required columns onto master
    master = master.merge(geography, on=['state_name', 'district_name'], how='left')
    master = master.merge(indices[['state_name', 'district_name', 'Overall_MAI']], on=['state_name', 'district_name'], how='left')
    master = master.merge(gap[['state_name', 'district_name', 'Latent_Demand_Gap']], on=['state_name', 'district_name'], how='left')
    
    # Load shapefile
    gpkg_path = os.path.join(RAW_DIR, '01_geography', 'district.gpkg')
    gdf = gpd.read_file(gpkg_path)
    
    # Convert IDs to string for safe merge
    master['pc11_state_id'] = master['pc11_state_id'].astype(str).str.zfill(2)
    master['pc11_district_id'] = master['pc11_district_id'].astype(str).str.zfill(3)
    gdf['pc11_state_id'] = gdf['pc11_state_id'].astype(str).str.zfill(2)
    gdf['pc11_district_id'] = gdf['pc11_district_id'].astype(str).str.zfill(3)
    
    # Merge map with master
    gdf = gdf.merge(master, on=['pc11_state_id', 'pc11_district_id'], how='inner')
    
    # Drop any rows where geometry or target variables are missing
    gdf = gdf.dropna(subset=['geometry', 'Overall_MAI', 'Latent_Demand_Gap'])
    
    print(f"Loaded GeoDataFrame with {len(gdf)} districts.")
    
    # ── 2. Build Spatial Weights Matrix ──
    # Queen contiguity (districts sharing a border/vertex are neighbors)
    w = libpysal.weights.Queen.from_dataframe(gdf)
    
    # Handle islands if any (districts with no neighbors)
    if w.islands:
        print(f"\nFound {len(w.islands)} island(s) with no neighbors. Removing them to compute Moran's I.")
        gdf = gdf.drop(w.islands).reset_index(drop=True)
        w = libpysal.weights.Queen.from_dataframe(gdf)
        
    # Row-standardize the weights matrix
    w.transform = 'r'
    
    # ── 3. Compute Moran's I ──
    # --- Overall MAI ---
    y_mai = gdf['Overall_MAI'].values
    moran_mai = esda.Moran(y_mai, w, permutations=999)
    
    print("\n--- Moran's I: Overall_MAI ---")
    print(f"I-Statistic: {moran_mai.I:.4f}")
    print(f"Expected I (Randomness): {moran_mai.EI:.4f}")
    print(f"p-value (999 permutations): {moran_mai.p_sim:.4f}")
    
    # --- Latent Demand Gap ---
    y_gap = gdf['Latent_Demand_Gap'].values
    moran_gap = esda.Moran(y_gap, w, permutations=999)
    
    print("\n--- Moran's I: Latent_Demand_Gap ---")
    print(f"I-Statistic: {moran_gap.I:.4f}")
    print(f"Expected I (Randomness): {moran_gap.EI:.4f}")
    print(f"p-value (999 permutations): {moran_gap.p_sim:.4f}")
    
    # ── 4. Generate Scatterplot ──
    # Generate scatterplot for Overall MAI as the primary visualization
    fig, ax = plot_moran(moran_mai, zstandard=True)
    plt.suptitle("Moran Scatterplot - Overall MAI", fontsize=16)
    plt.tight_layout()
    plot_path = os.path.join(VIS_DIR, 'morans_i_scatterplot.png')
    fig.savefig(plot_path, dpi=300)
    plt.close(fig)
    print(f"\n✅ Saved Moran's I Scatterplot to {plot_path}")
    
    # ── 5. Plain-English Interpretation ──
    print("\n" + "="*60)
    print("  INTERPRETATION & BUSINESS IMPLICATION")
    print("="*60)
    
    def interpret_moran(moran_obj, metric_name):
        sig = "statistically significant" if moran_obj.p_sim < 0.05 else "not statistically significant"
        clustered = "positive spatial autocorrelation (clustering)" if moran_obj.I > 0 else "negative spatial autocorrelation (dispersion)"
        
        print(f"\nFor {metric_name}:")
        print(f"- The Moran's I is {moran_obj.I:.3f} with a p-value of {moran_obj.p_sim:.3f}.")
        print(f"- This indicates {sig} {clustered}.")
        if moran_obj.p_sim < 0.05 and moran_obj.I > 0:
            print(f"- Meaning: High-scoring districts are surrounded by other high-scoring districts, and low-scoring districts are surrounded by low ones.")
            
    interpret_moran(moran_mai, "Overall MAI")
    interpret_moran(moran_gap, "Latent Demand Gap")
    
    print("\nWhat does this mean for the 'districts aren't independent' story?")
    print("Because districts share borders, economic spillovers, and regional infrastructure, their market attractiveness and gaps are highly correlated spatially.")
    print("Therefore, treating each district as an isolated market (the standard i.i.d. assumption) is flawed. Regional hub-and-spoke models or state-level corridors will be more effective than scattered, isolated investments.")

if __name__ == '__main__':
    main()
