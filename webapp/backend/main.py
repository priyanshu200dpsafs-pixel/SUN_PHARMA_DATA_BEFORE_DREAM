from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import pandas as pd
import geopandas as gpd
import joblib
import json
import os
import time

app = FastAPI(title="Sun Pharma Market Attractiveness API")

# GZip compress all responses > 500 bytes (74MB GeoJSON → ~800KB over the wire)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
CODE_DIR = os.path.join(BASE_DIR, 'code')
PROCESSED_DIR = os.path.join(BASE_DIR, 'processed_data')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
GEOGRAPHY_DIR = os.path.join(BASE_DIR, 'raw_data', '01_geography')

# Global variables to hold data in memory
db = {}

@app.on_event("startup")
def load_data():
    print("Loading datasets into memory...")
    
    # 1. Load ML Model
    db['model'] = joblib.load(os.path.join(OUTPUTS_DIR, 'models', 'xgb_latent_demand.pkl'))
    
    # 2. Load Core Datasets
    master = pd.read_csv(os.path.join(PROCESSED_DIR, 'master_table_imputed.csv'))
    indices = pd.read_csv(os.path.join(OUTPUTS_DIR, 'final_indices.csv'))
    momentum = pd.read_csv(os.path.join(OUTPUTS_DIR, 'momentum_and_quadrants.csv'))
    gap = pd.read_csv(os.path.join(OUTPUTS_DIR, 'latent_demand_gap_v2.csv'))
    shap_vals = pd.read_csv(os.path.join(OUTPUTS_DIR, 'shap_values.csv'))
    shap_exps = pd.read_csv(os.path.join(OUTPUTS_DIR, 'shap_explanations.csv'))
    
    # Merge for frontend convenience
    df = pd.merge(indices, momentum[['district_name', 'state_name', 'Momentum_Score', 'Quadrant']], on=['district_name', 'state_name'])
    
    # Bring in extra raw features for the Spotlight Panel
    cols_to_add = ['district_name', 'state_name', 'macro_population', 'infra_hospitals_count', 'chronic_diabetes_prevalence', 'climate_rainfall_annual_mm', 'macro_economic_establishments']
    df = pd.merge(df, master[cols_to_add], on=['district_name', 'state_name'])
    db['plot_data'] = df
    db['master'] = master
    db['gap'] = gap
    db['shap_vals'] = shap_vals
    db['shap_exps'] = shap_exps
    
    print("Data loaded. Processing Geography...")
    
    # 3. Load Geography
    t0 = time.time()
    gdf = gpd.read_file(os.path.join(GEOGRAPHY_DIR, 'district.gpkg'))
    gdf = gdf.to_crs(epsg=4326)
    
    # PERFORMANCE: Simplify geometry from 74MB → ~4MB (97% reduction)
    # tolerance=0.005 degrees ≈ 500m – preserves district shapes but removes GPS noise
    gdf['geometry'] = gdf.geometry.simplify(tolerance=0.005, preserve_topology=True)
    print(f"Geometry simplified in {time.time()-t0:.1f}s")
    
    # Map raw geometry to correct state names to prevent cross-state duplicates (e.g. Aurangabad)
    geo_master = pd.read_csv(os.path.join(PROCESSED_DIR, 'geography_master.csv'))
    gdf['pc11_state_id'] = gdf['pc11_state_id'].astype(int)
    gdf['pc11_district_id'] = gdf['pc11_district_id'].astype(int)
    gdf = pd.merge(gdf, geo_master[['pc11_state_id', 'pc11_district_id', 'state_name']], on=['pc11_state_id', 'pc11_district_id'], how='left')
    
    gdf['district_name'] = gdf['district_name'].str.upper()
    gdf['state_name'] = gdf['state_name'].str.upper()
    
    # Merge plotting data onto geometry for the choropleth
    gdf_merged = gdf.merge(df, on=['state_name', 'district_name'], how='left')
    
    # Calculate geometric centroids BEFORE simplification for accuracy
    gdf_merged['lat'] = gdf_merged.geometry.centroid.y
    gdf_merged['lon'] = gdf_merged.geometry.centroid.x
    
    gdf_merged.set_index('district_name', inplace=True)
    
    # Pre-serialize GeoJSON to a string once at startup (avoids re-serializing on every request)
    db['geojson_str'] = gdf_merged.to_json()
    
    # Safely convert map_data to dict without NaN
    raw_map_data = gdf_merged.reset_index().drop(columns=['geometry']).to_dict(orient='records')
    safe_map_data = []
    for row in raw_map_data:
        safe_map_data.append({k: (None if pd.isna(v) else v) for k, v in row.items()})
    db['map_data'] = safe_map_data
    
    # Pre-serialize the scatter_data once at startup
    db['scatter_data_list'] = db['plot_data'].to_dict(orient='records')
    
    # Pre-build the entire dashboard_data JSON string (avoids re-serializing 4MB+ on every request)
    full_response = {
        "map_data": safe_map_data,
        "geojson": json.loads(db['geojson_str']),
        "scatter_data": db['scatter_data_list']
    }
    db['dashboard_json'] = json.dumps(full_response)
    
    print(f"Startup complete in {time.time()-t0:.1f}s! Response pre-cached ({len(db['dashboard_json'])/(1024*1024):.1f} MB, will be ~{len(db['dashboard_json'])/(1024*1024)/10:.1f} MB gzipped)")

@app.get("/api/ping")
def ping():
    return {"status": "online"}

@app.get("/api/dashboard_data")
def get_dashboard_data():
    """Returns pre-cached JSON blob. No serialization cost per request."""
    return Response(
        content=db['dashboard_json'],
        media_type="application/json"
    )

@app.get("/api/district/{state_name}/{dist_name}")
def get_district_details(state_name: str, dist_name: str):
    """Returns all deep-dive data for a specific district."""
    state_name = state_name.upper()
    dist_name = dist_name.upper()
    
    try:
        d_plot = db['plot_data'][(db['plot_data']['district_name'] == dist_name) & (db['plot_data']['state_name'] == state_name)].iloc[0].to_dict()
        d_gap = db['gap'][(db['gap']['district_name'] == dist_name) & (db['gap']['state_name'] == state_name)]
        gap_score = float(d_gap.iloc[0]['Latent_Demand_Gap']) if len(d_gap) > 0 else 0.0
        
        # Explainability
        exp_row = db['shap_exps'][(db['shap_exps']['district_name'] == dist_name) & (db['shap_exps']['state_name'] == state_name)]
        explanation = exp_row.iloc[0]['explanation'] if len(exp_row) > 0 else None
        
        # SHAP Bar Chart Data
        s_vals_df = db['shap_vals'][(db['shap_vals']['district_name'] == dist_name) & (db['shap_vals']['state_name'] == state_name)]
        shap_features = []
        if len(s_vals_df) > 0:
            s_vals = s_vals_df.iloc[0]
            s_cols = [c for c in s_vals.index if c.endswith('_shap')]
            for c in s_cols:
                feat_name = c.replace('macro_', '').replace('chronic_', '').replace('_shap', '')
                shap_features.append({"Feature": feat_name, "Impact": float(s_vals[c])})
                
        return {
            "metrics": d_plot,
            "gap_score": gap_score,
            "explanation": explanation,
            "shap_features": shap_features
        }
    except IndexError:
        raise HTTPException(status_code=404, detail="District not found")


class SimulationRequest(BaseModel):
    state_name: str
    dist_name: str
    pop_growth: float
    emp_growth: float
    est_growth: float
    dia_growth: float

@app.post("/api/simulate")
def simulate(req: SimulationRequest):
    """Runs live XGBoost inference based on slider shocks."""
    state_name = req.state_name.upper()
    dist_name = req.dist_name.upper()
    
    try:
        master = db['master']
        d_master = master[(master['district_name'] == dist_name) & (master['state_name'] == state_name)].iloc[0]
        
        features = [
            'macro_nightlights_mean', 'macro_economic_employees', 'macro_literacy_rate', 
            'macro_population', 'macro_economic_establishments',
            'chronic_diabetes_prevalence', 'chronic_hypertension_prevalence'
        ]
        
        base_X = d_master[features].to_frame().T.astype(float)
        base_pred = float(db['model'].predict(base_X)[0])
        actual_infra = float(d_master['infra_hospitals_count'] + d_master['infra_phc_chc_count'])
        
        # Apply shocks
        sim_X = base_X.copy()
        sim_X['macro_population'] *= (1 + req.pop_growth/100.0)
        sim_X['macro_economic_employees'] *= (1 + req.emp_growth/100.0)
        sim_X['macro_economic_establishments'] *= (1 + req.est_growth/100.0)
        sim_X['chronic_diabetes_prevalence'] += req.dia_growth
        
        sim_pred = float(db['model'].predict(sim_X)[0])
        
        return {
            "actual_infra": actual_infra,
            "base_pred": base_pred,
            "sim_pred": sim_pred,
            "sim_unmet_need": max(0.0, sim_pred - actual_infra)
        }
    except IndexError:
        raise HTTPException(status_code=404, detail="District not found")

from fastapi.staticfiles import StaticFiles

# Serve the static built React app
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, 'webapp/frontend/dist'), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)
