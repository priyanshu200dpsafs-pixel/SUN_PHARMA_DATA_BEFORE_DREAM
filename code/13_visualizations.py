"""
13_visualizations.py
Generates 6 interactive world-class Plotly visualizations for the project.
"""
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import os
import json

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR   = os.path.join(BASE_DIR, 'raw_data')
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')
VIS_DIR   = os.path.join(OUT_DIR, 'visuals')

os.makedirs(VIS_DIR, exist_ok=True)

# Color palettes
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
QUADRANT_COLORS = {
    'Invest Now': OKABE_ITO[0], # Orange
    'Emerging': OKABE_ITO[1],   # Light Blue
    'Harvest': OKABE_ITO[2],    # Green
    'Watch': OKABE_ITO[4]       # Dark Blue
}
CONFIDENCE_COLORS = {
    'HIGH': OKABE_ITO[2],       # Green
    'MEDIUM': OKABE_ITO[0],     # Orange
    'LOW': OKABE_ITO[5]         # Red/Vermillion
}

def load_data():
    master = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))
    geography = pd.read_csv(os.path.join(PROC_DIR, 'geography_master.csv'))
    indices = pd.read_csv(os.path.join(OUT_DIR, 'final_indices.csv'))
    momentum = pd.read_csv(os.path.join(OUT_DIR, 'momentum_and_quadrants.csv'))
    gap = pd.read_csv(os.path.join(OUT_DIR, 'latent_demand_gap_v2.csv'))
    shap_vals = pd.read_csv(os.path.join(OUT_DIR, 'shap_values.csv'))
    
    # Pre-process master for map (needs pc11 ids)
    master = master.merge(geography, on=['state_name', 'district_name'], how='left')
    
    gpkg_path = os.path.join(RAW_DIR, '01_geography', 'district.gpkg')
    gdf = gpd.read_file(gpkg_path)
    
    # For Plotly choropleth_mapbox, reproject to WGS84
    gdf = gdf.to_crs(epsg=4326)
    
    # Convert object ids to string for safe merge
    master['pc11_state_id'] = master['pc11_state_id'].astype(str).str.zfill(2)
    master['pc11_district_id'] = master['pc11_district_id'].astype(str).str.zfill(3)
    gdf['pc11_state_id'] = gdf['pc11_state_id'].astype(str).str.zfill(2)
    gdf['pc11_district_id'] = gdf['pc11_district_id'].astype(str).str.zfill(3)
    
    # Merge map with master
    gdf = gdf.drop(columns=['district_name']).merge(master, on=['pc11_state_id', 'pc11_district_id'], how='left')
    
    return master, indices, momentum, gap, shap_vals, gdf

def main():
    print("="*60)
    print("  VISUALIZATION ENGINE (Plotly Interactive)")
    print("="*60)
    
    master, indices, momentum, gap, shap_vals, gdf = load_data()
    
    # Merge datasets for easier plotting
    df_plot = indices.merge(momentum[['district_name', 'state_name', 'Momentum_Score', 'Quadrant']], on=['state_name', 'district_name'])
    df_plot = df_plot.merge(master[['state_name', 'district_name', 'macro_population', 'data_confidence_tier']], on=['state_name', 'district_name'])
    df_gap = gap.merge(master[['state_name', 'district_name', 'data_confidence_tier']], on=['state_name', 'district_name'])
    
    # Update gdf with the values we want to map
    gdf = gdf.merge(indices[['district_name', 'state_name', 'Overall_MAI', 'Chronic_MAI', 'Acute_MAI']], on=['state_name', 'district_name'], how='left')
    
    # Create GeoJSON from gdf
    gdf_json = json.loads(gdf.to_json())
    gdf['id'] = gdf.index # Plotly needs an ID
    
    # 1. interactive_choropleth_overall.html
    print("Generating 1. interactive_choropleth_overall.html...")
    fig1 = px.choropleth_mapbox(
        gdf, geojson=gdf_json, locations=gdf.index, color='Overall_MAI',
        hover_name='district_name', hover_data=['state_name', 'Overall_MAI', 'Chronic_MAI', 'Acute_MAI', 'data_confidence_tier'],
        color_continuous_scale='viridis', range_color=(0, 100),
        mapbox_style="carto-positron", zoom=3.5, center={"lat": 22.0, "lon": 79.0}
    )
    fig1.update_layout(
        title=dict(text="District-Level Overall Market Attractiveness Index", font=dict(size=24)),
        margin=dict(r=20, t=80, l=20, b=20),
        coloraxis_colorbar=dict(title="Overall MAI")
    )
    fig1.write_html(os.path.join(VIS_DIR, 'interactive_choropleth_overall.html'))

    # 2. interactive_quadrant_scatter.html
    print("Generating 2. interactive_quadrant_scatter.html...")
    fig2 = px.scatter(
        df_plot, x='Overall_MAI', y='Momentum_Score',
        color='Quadrant', size='macro_population', hover_name='district_name',
        hover_data=['state_name', 'Overall_MAI', 'Momentum_Score', 'macro_population', 'data_confidence_tier'],
        color_discrete_map=QUADRANT_COLORS,
        labels={'Overall_MAI': 'Overall MAI Score (Current Market Scale)', 'Momentum_Score': 'Momentum Score (Future Growth Trajectory)'}
    )
    fig2.add_vline(x=50, line_width=1, line_dash="dash", line_color="black")
    fig2.add_hline(y=0, line_width=1, line_dash="dash", line_color="black")
    fig2.update_layout(
        title=dict(text="District Trajectory: Current Scale vs. Future Momentum", font=dict(size=24)),
        margin=dict(r=150, t=80, l=50, b=50),
        legend=dict(title="Quadrant", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, font=dict(size=14))
    )
    fig2.write_html(os.path.join(VIS_DIR, 'interactive_quadrant_scatter.html'))

    # 3. latent_demand_gap_3d.html
    print("Generating 3. latent_demand_gap_3d.html...")
    valid_gap = df_gap[df_gap['macro_population'] >= 500000]
    fig3 = px.scatter_3d(
        valid_gap, x='predicted_infra_percentile', y='actual_infra_percentile', z='macro_population',
        color='Latent_Demand_Gap', hover_name='district_name',
        hover_data=['state_name', 'Latent_Demand_Gap'],
        color_continuous_scale='viridis',
        labels={
            'predicted_infra_percentile': 'Expected Infra %tile',
            'actual_infra_percentile': 'Actual Infra %tile',
            'macro_population': 'Population',
            'Latent_Demand_Gap': 'Gap Score'
        }
    )
    fig3.update_traces(marker=dict(size=5))
    fig3.update_layout(
        title=dict(text="Latent Demand Gap (Pop > 500k): Expected vs Actual Infra", font=dict(size=24)),
        margin=dict(r=20, t=80, l=20, b=20)
    )
    fig3.write_html(os.path.join(VIS_DIR, 'latent_demand_gap_3d.html'))

    # 4. confidence_map.html
    print("Generating 4. confidence_map.html...")
    fig4 = px.choropleth_mapbox(
        gdf, geojson=gdf_json, locations=gdf.index, color='data_confidence_tier',
        hover_name='district_name', hover_data=['state_name'],
        color_discrete_map=CONFIDENCE_COLORS,
        mapbox_style="carto-positron", zoom=3.5, center={"lat": 22.0, "lon": 79.0}
    )
    fig4.update_layout(
        title=dict(text="Data Confidence Tier by District", font=dict(size=24)),
        margin=dict(r=20, t=80, l=20, b=20),
        legend=dict(title="Confidence Tier")
    )
    fig4.write_html(os.path.join(VIS_DIR, 'confidence_map.html'))

    # 5. shap_summary_interactive.html
    print("Generating 5. shap_summary_interactive.html...")
    shap_cols = [c for c in shap_vals.columns if c.endswith('_shap')]
    mean_abs_shap = shap_vals[shap_cols].abs().mean().sort_values(ascending=True)
    shap_df_agg = mean_abs_shap.reset_index()
    shap_df_agg.columns = ['Feature', 'Mean Absolute SHAP']
    shap_df_agg['Feature'] = shap_df_agg['Feature'].str.replace('_shap', '')
    
    fig5 = px.bar(
        shap_df_agg, x='Mean Absolute SHAP', y='Feature', orientation='h',
        color='Mean Absolute SHAP', color_continuous_scale='viridis'
    )
    fig5.update_layout(
        title=dict(text="SHAP Feature Importance (Expected Infrastructure)", font=dict(size=24)),
        margin=dict(r=50, t=80, l=200, b=50)
    )
    fig5.write_html(os.path.join(VIS_DIR, 'shap_summary_interactive.html'))

    # 6. top20_ranking_chart.html
    print("Generating 6. top20_ranking_chart.html...")
    top20 = df_plot.sort_values('Overall_MAI', ascending=False).head(20)
    top20 = top20.sort_values('Overall_MAI', ascending=True)
    top20['Label'] = top20['district_name'] + " (" + top20['state_name'] + ")"
    
    fig6 = px.bar(
        top20, x='Overall_MAI', y='Label', orientation='h',
        color='Overall_MAI', color_continuous_scale='viridis',
        labels={'Overall_MAI': 'Overall MAI Score', 'Label': 'District'}
    )
    fig6.update_layout(
        title=dict(text="Top 20 Districts: Overall Market Attractiveness", font=dict(size=24)),
        margin=dict(r=50, t=80, l=250, b=50)
    )
    fig6.write_html(os.path.join(VIS_DIR, 'top20_ranking_chart.html'))
    
    print(f"\n✅ All visuals saved to {VIS_DIR}/")

if __name__ == '__main__':
    main()
