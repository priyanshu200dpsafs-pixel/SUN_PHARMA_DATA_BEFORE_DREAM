"""
11b_latent_demand_gap.py

Trains an XGBoost Regressor to predict expected infrastructure capacity 
based on macro-economic scale and chronic disease burden.
Calculates the Latent Demand Gap (where expected > actual).
"""

import pandas as pd
import numpy as np
import os
import xgboost as xgb
import joblib
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import mean_squared_error

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')

def main():
    print("="*60)
    print("  LATENT DEMAND GAP ANALYSIS V2 (INFRASTRUCTURE TARGET)")
    print("="*60)
    
    # Load data
    df = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))
    
    # ── STEP 1: Compute Target and Define Features ──
    # Target: Raw infrastructure capacity
    df['infra_raw'] = df['infra_hospitals_count'] + df['infra_phc_chc_count']
    y = df['infra_raw']
    
    features = [
        'macro_nightlights_mean', 
        'macro_economic_employees', 
        'macro_literacy_rate', 
        'macro_population', 
        'macro_economic_establishments',
        'chronic_diabetes_prevalence',
        'chronic_hypertension_prevalence'
    ]
    X = df[features]
    
    model_path = os.path.join(OUT_DIR, 'models', 'xgb_latent_demand.pkl')
    if os.path.exists(model_path):
        print(f"Loading tuned model from {model_path}...")
        model = joblib.load(model_path)
    else:
        print("Training new baseline model...")
        model = xgb.XGBRegressor(
            n_estimators=100, 
            learning_rate=0.1, 
            max_depth=4, 
            random_state=42
        )
        
        # 5-Fold CV for honest validation
        cv_r2 = cross_val_score(model, X, y, cv=5, scoring='r2')
        cv_preds = cross_val_predict(model, X, y, cv=5)
        cv_rmse = np.sqrt(mean_squared_error(y, cv_preds))
        
        print("XGBoost Model Performance (5-Fold CV):")
        print(f"  Mean R²: {cv_r2.mean():.4f} (Std: {cv_r2.std():.4f})")
        print(f"  RMSE:    {cv_rmse:.4f}")
        
        # Train on full dataset
        model.fit(X, y)
        
        # Save the model
        model_dir = os.path.join(OUT_DIR, 'models')
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(model, model_path)
        print(f"✅ Saved XGBoost model to {model_path}")
    
    print("\nFeature Importances:")
    importances = model.feature_importances_
    feat_imp = pd.DataFrame({'Feature': features, 'Importance': importances}).sort_values('Importance', ascending=False)
    for _, row in feat_imp.iterrows():
        print(f"  {row['Feature']}: {row['Importance']:.4f}")
        
    # ── STEP 2: Compute the Gap ──
    # Predict for all districts
    df['predicted_infra'] = model.predict(X)
    
    # Percentile ranks
    df['predicted_infra_percentile'] = df['predicted_infra'].rank(pct=True) * 100
    df['actual_infra_percentile'] = df['infra_raw'].rank(pct=True) * 100
    
    # Gap Score = Expected Infra Rank - Actual Infra Rank
    df['Latent_Demand_Gap'] = df['predicted_infra_percentile'] - df['actual_infra_percentile']
    
    # ── STEP 3: Output ──
    out_cols = [
        'state_name', 'district_name', 
        'macro_population',
        'predicted_infra_percentile', 
        'actual_infra_percentile', 
        'Latent_Demand_Gap'
    ]
    df_out = df[out_cols].sort_values('Latent_Demand_Gap', ascending=False)
    
    print("\n🚀 TOP 20 DISTRICTS BY LATENT DEMAND GAP (Pop > 500k)")
    valid_districts = df_out[df_out['macro_population'] >= 500000]
    for i, r in enumerate(valid_districts.head(20).itertuples(), 1):
        pop_millions = r.macro_population / 1000000.0
        print(f"  {i}. {r.district_name} ({r.state_name}) | Pop: {pop_millions:.2f}M | Gap: +{r.Latent_Demand_Gap:.1f} pts (Expected Infra %tile: {r.predicted_infra_percentile:.1f}, Actual Infra %tile: {r.actual_infra_percentile:.1f})")
        
    out_path = os.path.join(OUT_DIR, 'latent_demand_gap_v2.csv')
    df_out.to_csv(out_path, index=False)
    print(f"\n✅ Saved to {out_path}")
    
    # Note: Model saving handled in training block.

if __name__ == '__main__':
    main()
