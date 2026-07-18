"""
14_streamlit_dashboard.py
Interactive Streamlit Dashboard for Sun Pharma Market Attractiveness.
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import json
import time
import geopandas as gpd
import plotly.express as px

# --- PATHS ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROC_DIR = os.path.join(BASE_DIR, '../processed_data')
OUT_DIR = os.path.join(BASE_DIR, '../outputs')
RAW_DIR = os.path.join(BASE_DIR, '../raw_data')

# --- CONFIG & THEME ---
st.set_page_config(page_title="Sun Pharma Market Attractiveness", layout="wide")

st.markdown("""
    <style>
        /* Force background and standard text colors */
        .stApp {
            background-color: #FAFAFA;
            color: #1E1E1E;
        }
        
        /* Tighten default padding to prevent unnecessary vertical scrolling */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }
        
        /* Custom Executive Card Components with soft shadows */
        div[data-testid="stMetricContainer"] {
            background-color: #FFFFFF !important;
            border: 1px solid #EAEAEA !important;
            padding: 20px 24px !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        div[data-testid="stMetricContainer"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
        }
        
        /* Sidebar styling optimization */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #EAEAEA !important;
        }
        
        /* Clean text adjustments */
        h1, h2, h3 {
            color: #111827 !important;
            font-family: 'Inter', -apple-system, sans-serif !important;
            font-weight: 700 !important;
        }

        /* Value & Metric text adjustments for light theme */
        div[data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #111827;
        }

        /* Preserve Custom Badges */
        .badge-high { background-color: #009E73; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .badge-medium { background-color: #E69F00; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .badge-low { background-color: #D55E00; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        
        .quad-invest { background-color: #E69F00; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .quad-emerging { background-color: #56B4E9; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .quad-harvest { background-color: #009E73; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .quad-watch { background-color: #0072B2; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Color palettes
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
QUADRANT_COLORS = {'Invest Now': OKABE_ITO[0], 'Emerging': OKABE_ITO[1], 'Harvest': OKABE_ITO[2], 'Watch': OKABE_ITO[4]}

# --- DATA CACHING ---
@st.cache_data
def load_data():
    master = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))
    geography = pd.read_csv(os.path.join(PROC_DIR, 'geography_master.csv'))
    indices = pd.read_csv(os.path.join(OUT_DIR, 'final_indices.csv'))
    momentum = pd.read_csv(os.path.join(OUT_DIR, 'momentum_and_quadrants.csv'))
    gap = pd.read_csv(os.path.join(OUT_DIR, 'latent_demand_gap_v2.csv'))
    shap_vals = pd.read_csv(os.path.join(OUT_DIR, 'shap_values.csv'))
    shap_exps = pd.read_csv(os.path.join(OUT_DIR, 'shap_explanations.csv'))
    
    # Merge for easier plotting
    df_plot = indices.merge(momentum[['district_name', 'state_name', 'Momentum_Score', 'Quadrant']], on=['state_name', 'district_name'])
    df_plot = df_plot.merge(master[['state_name', 'district_name', 'macro_population', 'data_confidence_tier']], on=['state_name', 'district_name'])
    
    # Load and prep map
    master_geo = master.merge(geography, on=['state_name', 'district_name'], how='left')
    gpkg_path = os.path.join(RAW_DIR, '01_geography', 'district.gpkg')
    gdf = gpd.read_file(gpkg_path).to_crs(epsg=4326)
    
    master_geo['pc11_state_id'] = master_geo['pc11_state_id'].astype(str).str.zfill(2)
    master_geo['pc11_district_id'] = master_geo['pc11_district_id'].astype(str).str.zfill(3)
    gdf['pc11_state_id'] = gdf['pc11_state_id'].astype(str).str.zfill(2)
    gdf['pc11_district_id'] = gdf['pc11_district_id'].astype(str).str.zfill(3)
    
    gdf = gdf.drop(columns=['district_name']).merge(master_geo, on=['pc11_state_id', 'pc11_district_id'], how='left')
    gdf = gdf.merge(indices[['district_name', 'state_name', 'Overall_MAI', 'Chronic_MAI', 'Acute_MAI']], on=['state_name', 'district_name'], how='left')
    
    gdf_json = json.loads(gdf.to_json())
    gdf['id'] = gdf.index
    
    return master, df_plot, gap, shap_vals, shap_exps, gdf, gdf_json

@st.cache_resource
def load_model():
    return joblib.load(os.path.join(OUT_DIR, 'models', 'xgb_latent_demand.pkl'))

master, df_plot, gap, shap_vals, shap_exps, gdf, gdf_json = load_data()
model = load_model()

# --- SIDEBAR NAV ---
st.sidebar.title("Navigation")
view = st.sidebar.radio("Select View:", [
    "1. National Overview", 
    "2. District Deep-Dive", 
    "3. What-If Simulator", 
    "4. Rankings & Explorer"
])

# ---------------------------------------------------------
# VIEW 1: NATIONAL OVERVIEW
# ---------------------------------------------------------
if view == "1. National Overview":
    st.title("National Market Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Districts", len(df_plot))
    with col2:
        st.metric("Avg Overall MAI", f"{df_plot['Overall_MAI'].mean():.1f}")
    with col3:
        st.metric("Invest Now Districts", len(df_plot[df_plot['Quadrant'] == 'Invest Now']))
    with col4:
        st.metric("XGBoost Model R²", "0.559")
        
    st.divider()
    
    # Map
    st.subheader("Interactive Market Attractiveness Map")
    map_metric = st.selectbox("Select Metric to Map:", ["Overall_MAI", "Chronic_MAI", "Acute_MAI"])
    
    @st.cache_data
    def create_map_figure(metric, _gdf, _gdf_json):
        fig = px.choropleth_mapbox(
            _gdf, geojson=_gdf_json, locations=_gdf.index, color=metric,
            hover_name='district_name', hover_data=['state_name', 'Overall_MAI', 'Chronic_MAI', 'Acute_MAI', 'data_confidence_tier'],
            color_continuous_scale='viridis', range_color=(0, 100),
            mapbox_style="carto-positron", zoom=3.5, center={"lat": 22.0, "lon": 79.0}
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig

    fig_map = create_map_figure(map_metric, gdf, gdf_json)
    st.plotly_chart(fig_map)
    
    # Scatter
    st.subheader("District Trajectory: Scale vs Momentum")
    
    @st.cache_data
    def create_scatter_figure(_df_plot, _colors):
        fig = px.scatter(
            _df_plot, x='Overall_MAI', y='Momentum_Score',
            color='Quadrant', size='macro_population', hover_name='district_name',
            hover_data=['state_name', 'Overall_MAI', 'Momentum_Score'],
            color_discrete_map=_colors,
            labels={'Overall_MAI': 'Overall MAI Score', 'Momentum_Score': 'Momentum Score'}
        )
        fig.add_vline(x=50, line_width=1, line_dash="dash", line_color="#EAEAEA")
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#EAEAEA")
        fig.update_layout(height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#111827'))
        return fig

    fig_scatter = create_scatter_figure(df_plot, QUADRANT_COLORS)
    st.plotly_chart(fig_scatter)

# ---------------------------------------------------------
# VIEW 2: DISTRICT DEEP-DIVE
# ---------------------------------------------------------
elif view == "2. District Deep-Dive":
    st.title("District Deep-Dive")
    if 'state_selector' not in st.session_state:
        st.session_state.state_selector = "All States"
    if 'dist_selector' not in st.session_state:
        st.session_state.dist_selector = sorted((df_plot['district_name'] + " (" + df_plot['state_name'] + ")").tolist())[0]

    def on_state_change():
        state = st.session_state.state_selector
        if state != "All States":
            first_dist = sorted(df_plot[df_plot['state_name'] == state].apply(lambda x: f"{x['district_name']} ({x['state_name']})", axis=1).tolist())[0]
            st.session_state.dist_selector = first_dist
            
    def on_dist_change():
        dist_label = st.session_state.dist_selector
        actual_state = dist_label.split(" (")[1].replace(")", "")
        st.session_state.state_selector = actual_state

    states = ["All States"] + sorted(df_plot['state_name'].unique().tolist())
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        st.selectbox("Select State/UT", states, key="state_selector", on_change=on_state_change)
        
    with col_sel2:
        curr_state = st.session_state.state_selector
        if curr_state == "All States":
            districts_list = sorted((df_plot['district_name'] + " (" + df_plot['state_name'] + ")").tolist())
        else:
            df_sub = df_plot[df_plot['state_name'] == curr_state]
            districts_list = sorted((df_sub['district_name'] + " (" + df_sub['state_name'] + ")").tolist())
            
        st.selectbox("Search for a District", districts_list, key="dist_selector", on_change=on_dist_change)
        
    selected_dist_label = st.session_state.dist_selector
    dist_name = selected_dist_label.split(" (")[0]
    actual_state = selected_dist_label.split(" (")[1].replace(")", "")
    
    # Extract data
    d_plot = df_plot[(df_plot['district_name'] == dist_name) & (df_plot['state_name'] == actual_state)].iloc[0]
    d_gap = gap[(gap['district_name'] == dist_name) & (gap['state_name'] == actual_state)]
    gap_score = d_gap.iloc[0]['Latent_Demand_Gap'] if len(d_gap) > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric("Overall MAI", f"{d_plot['Overall_MAI']:.1f}", delta=f"{gap_score:.1f} Gap")
    with col2:
        with st.container(border=True):
            st.metric("Chronic MAI", f"{d_plot['Chronic_MAI']:.1f}")
    with col3:
        with st.container(border=True):
            st.metric("Acute MAI", f"{d_plot['Acute_MAI']:.1f}")
            
    # Badges
    st.write("---")
    st.write("### Diagnostics")
    c1, c2 = st.columns(2)
    conf = d_plot['data_confidence_tier']
    conf_class = f"badge-{conf.lower()}"
    quad = d_plot['Quadrant']
    quad_class = f"quad-{quad.lower().replace(' ', '')}"
    
    with c1:
        st.markdown(f"**Data Confidence:** <span class='{conf_class}'>{conf}</span>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**Market Strategy:** <span class='{quad_class}'>{quad}</span>", unsafe_allow_html=True)
        
    # SHAP Explainability
    st.write("---")
    st.subheader("Machine Learning Insights")
    
    exp_row = shap_exps[(shap_exps['district_name'] == dist_name) & (shap_exps['state_name'] == actual_state)]
    if len(exp_row) > 0:
        st.info("💡 " + exp_row.iloc[0]['explanation'])
    else:
        st.info("💡 Insight narrative not available for this district (Outside Top 10 bounds).")
        
    # SHAP Bar Chart
    s_vals_df = shap_vals[(shap_vals['district_name'] == dist_name) & (shap_vals['state_name'] == actual_state)]
    if len(s_vals_df) > 0:
        s_vals = s_vals_df.iloc[0]
        s_cols = [c for c in s_vals.index if c.endswith('_shap')]
        s_df = pd.DataFrame({'Feature': [c.replace('macro_', '').replace('chronic_', '').replace('_shap', '') for c in s_cols], 'Impact': s_vals[s_cols].values})
        s_df = s_df.sort_values('Impact')
        
        fig_shap = px.bar(s_df, x='Impact', y='Feature', orientation='h', title=f"SHAP Drivers for {dist_name}", color='Impact', color_continuous_scale='viridis')
        fig_shap.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#111827'))
        st.plotly_chart(fig_shap)

# ---------------------------------------------------------
# VIEW 3: WHAT-IF SIMULATOR
# ---------------------------------------------------------
elif view == "3. What-If Simulator":
    st.title("What-If Infrastructure Simulator")
    st.write("Stress-test the XGBoost model by simulating macroeconomic shocks to a district.")
    
    districts_list = df_plot['district_name'] + " (" + df_plot['state_name'] + ")"
    selected = st.selectbox("Select District to Simulate", sorted(districts_list.tolist()))
    dist_name = selected.split(" (")[0]
    
    # Get raw features
    features = [
        'macro_nightlights_mean', 'macro_economic_employees', 'macro_literacy_rate', 
        'macro_population', 'macro_economic_establishments',
        'chronic_diabetes_prevalence', 'chronic_hypertension_prevalence'
    ]
    
    d_master = master[master['district_name'] == dist_name].iloc[0]
    actual_infra = d_master['infra_hospitals_count'] + d_master['infra_phc_chc_count']
    
    base_X = d_master[features].to_frame().T.astype(float)
    base_pred = model.predict(base_X)[0]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Macro Shocks")
        pop_growth = st.slider("Population Growth (%)", -50, 150, 0)
        emp_growth = st.slider("Economic Employees Growth (%)", -50, 150, 0)
        est_growth = st.slider("Economic Establishments Growth (%)", -50, 150, 0)
        dia_growth = st.slider("Diabetes Prev Shift (absolute %)", -5.0, 5.0, 0.0)
        
    with col2:
        st.subheader("Simulation Results")
        
        sim_X = base_X.copy()
        sim_X['macro_population'] *= (1 + pop_growth/100.0)
        sim_X['macro_economic_employees'] *= (1 + emp_growth/100.0)
        sim_X['macro_economic_establishments'] *= (1 + est_growth/100.0)
        sim_X['chronic_diabetes_prevalence'] += dia_growth
        
        sim_pred = model.predict(sim_X)[0]
        
        st.metric(
            label="Predicted Infrastructure Need (Raw Count)", 
            value=f"{sim_pred:.1f}", 
            delta=f"{sim_pred - base_pred:.1f} vs Baseline"
        )
        
        # Recalculate Gap
        st.write(f"**Actual Infrastructure Existing:** {actual_infra}")
        st.write(f"**Simulated Unmet Need (Gap Count):** {max(0, sim_pred - actual_infra):.1f}")
        
        # Simple Bar Chart
        comp_df = pd.DataFrame({
            'Scenario': ['Actual Existing', 'Baseline Prediction', 'Simulated Prediction'],
            'Count': [actual_infra, base_pred, sim_pred]
        })
        fig_sim = px.bar(comp_df, x='Scenario', y='Count', color='Scenario', text_auto='.1f', title="Infrastructure Gap Comparison")
        fig_sim.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#111827'), showlegend=False)
        st.plotly_chart(fig_sim)

# ---------------------------------------------------------
# VIEW 4: RANKINGS & EXPLORER
# ---------------------------------------------------------
elif view == "4. Rankings & Explorer":
    st.title("Data Explorer")
    
    cols_to_show = [
        'state_name', 'district_name', 'Overall_MAI', 'Chronic_MAI', 'Acute_MAI', 
        'Momentum_Score', 'Quadrant', 'macro_population'
    ]
    
    st.dataframe(df_plot[cols_to_show].sort_values('Overall_MAI', ascending=False), height=600)
    
    csv = df_plot[cols_to_show].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Dataset as CSV",
        data=csv,
        file_name='sun_pharma_final_rankings.csv',
        mime='text/csv',
    )
