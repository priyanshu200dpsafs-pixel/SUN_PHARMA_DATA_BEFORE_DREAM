"""
12_shap_explainability.py

Retrains the Latent Demand Gap XGBoost model, runs SHAP explanations on 
all districts, and generates plain-English narratives for top districts.
"""

import pandas as pd
import numpy as np
import os
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')

def main():
    print("="*60)
    print("  SHAP EXPLAINABILITY ENGINE")
    print("="*60)
    
    # ── 1. Reload & Retrain Model ──
    df = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))
    
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
    
    # Train or Load model
    import joblib
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
        model.fit(X, y)
    
    # ── 2. Run SHAP TreeExplainer ──
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    expected_value = explainer.expected_value
    if isinstance(expected_value, np.ndarray):
        expected_value = expected_value[0]
        
    # Save full SHAP values
    shap_df = pd.DataFrame(shap_values, columns=[f"{f}_shap" for f in features])
    shap_df['state_name'] = df['state_name']
    shap_df['district_name'] = df['district_name']
    
    out_shap_path = os.path.join(OUT_DIR, 'shap_values.csv')
    shap_df.to_csv(out_shap_path, index=False)
    print(f"✅ Saved full SHAP values to {out_shap_path}")
    
    # ── 3. SHAP Summary Plot ──
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)
    plt.tight_layout()
    plot_path = os.path.join(OUT_DIR, 'shap_summary_plot.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"✅ Saved SHAP summary plot to {plot_path}")
    
    # ── 4. Generate Plain-English Explanations ──
    # Get top 10 Latent Demand Gap (excluding pop < 500k)
    gap_df = pd.read_csv(os.path.join(OUT_DIR, 'latent_demand_gap_v2.csv'))
    gap_df = gap_df[gap_df['macro_population'] >= 500000].head(10)
    gap_districts = gap_df['district_name'].tolist()
    
    # Get top 10 Overall_MAI
    mai_df = pd.read_csv(os.path.join(OUT_DIR, 'final_indices.csv'))
    mai_df = mai_df.sort_values('Rank_Overall').head(10)
    mai_districts = mai_df['district_name'].tolist()
    
    target_districts = list(set(gap_districts + mai_districts))
    
    explanations = []
    
    for dist in target_districts:
        # Find index
        idx = df[df['district_name'] == dist].index[0]
        state = df.at[idx, 'state_name']
        
        # Total predicted value
        pred_val = expected_value + sum(shap_values[idx])
        if pred_val <= 0: pred_val = 1e-5 # prevent division by zero
        
        # Calculate % contribution to the predicted value
        contribs = {}
        for i, f in enumerate(features):
            short_name = f.replace('macro_', '').replace('chronic_', '')
            contrib_pct = (shap_values[idx][i] / pred_val) * 100
            contribs[short_name] = contrib_pct
            
        pos_drivers = [(k, v) for k, v in contribs.items() if v > 0]
        neg_drivers = [(k, v) for k, v in contribs.items() if v < 0]
        
        pos_drivers.sort(key=lambda x: x[1], reverse=True)
        neg_drivers.sort(key=lambda x: x[1])
        
        txt = f"{dist} ({state}): expected infrastructure driven primarily by "
        if len(pos_drivers) > 0:
            txt += f"{pos_drivers[0][0]} (+{pos_drivers[0][1]:.0f}%)"
        if len(pos_drivers) > 1:
            txt += f" and {pos_drivers[1][0]} (+{pos_drivers[1][1]:.0f}%)"
            
        if len(neg_drivers) > 0:
            txt += f", partially offset by {neg_drivers[0][0]} ({neg_drivers[0][1]:.0f}%)"
            
        # Determine why it was selected
        reason = []
        if dist in gap_districts: reason.append("Top Demand Gap")
        if dist in mai_districts: reason.append("Top Overall MAI")
        
        explanations.append({
            'district_name': dist,
            'state_name': state,
            'inclusion_reason': " & ".join(reason),
            'explanation': txt
        })
        
    exp_df = pd.DataFrame(explanations)
    exp_path = os.path.join(OUT_DIR, 'shap_explanations.csv')
    exp_df.to_csv(exp_path, index=False)
    print(f"✅ Saved SHAP plain-English explanations to {exp_path}")
    
    print("\nSAMPLE EXPLANATIONS:")
    for _, row in exp_df.head(5).iterrows():
        print(f"- {row['explanation']}")

if __name__ == '__main__':
    main()
