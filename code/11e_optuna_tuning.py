"""
11e_optuna_tuning.py

Tunes XGBoost hyperparameters for the Latent Demand Gap model using Optuna.
Generates visualizations of the optimization process, saves the tuned model, 
and triggers downstream processes (11b and 12).
"""

import pandas as pd
import numpy as np
import os
import xgboost as xgb
import optuna
import joblib
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import mean_squared_error
import optuna.visualization as vis
import subprocess

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')
VIS_DIR   = os.path.join(OUT_DIR, 'visuals')
MODEL_DIR = os.path.join(OUT_DIR, 'models')

# Create directories if they don't exist
os.makedirs(VIS_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

def main():
    print("="*60)
    print("  OPTUNA HYPERPARAMETER TUNING (XGBOOST)")
    print("="*60)
    
    # ── STEP 1: Load Data ──
    df = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))
    
    # Target
    df['infra_raw'] = df['infra_hospitals_count'] + df['infra_phc_chc_count']
    y = df['infra_raw']
    
    # Features
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
    
    # Baseline Metrics
    BASELINE_R2 = 0.559
    BASELINE_RMSE = 21.8
    
    # Optuna Objective
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'gamma': trial.suggest_float('gamma', 0.0, 5.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 5.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 5.0),
            'random_state': 42,
            'n_jobs': -1
        }
        
        model = xgb.XGBRegressor(**params)
        
        # 5-fold CV R2
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2', n_jobs=-1)
        return cv_scores.mean()

    # Run Optuna Study
    print("\nRunning Optuna optimization for 100 trials...")
    # Suppress verbose optuna logging except warnings to keep output clean
    optuna.logging.set_verbosity(optuna.logging.WARNING) 
    
    study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=100, show_progress_bar=True)
    
    best_params = study.best_params
    best_params['random_state'] = 42
    
    # ── STEP 2: Evaluate & Report ──
    print("\n=== TUNING RESULTS ===")
    print("Best Hyperparameters:")
    for k, v in best_params.items():
        if k != 'random_state':
            print(f"  {k}: {v}")
            
    # Train tuned model for final CV metrics
    tuned_model = xgb.XGBRegressor(**best_params)
    cv_r2_tuned = cross_val_score(tuned_model, X, y, cv=5, scoring='r2', n_jobs=-1)
    cv_preds_tuned = cross_val_predict(tuned_model, X, y, cv=5, n_jobs=-1)
    cv_rmse_tuned = np.sqrt(mean_squared_error(y, cv_preds_tuned))
    
    tuned_r2_mean = cv_r2_tuned.mean()
    
    print("\n=== PERFORMANCE COMPARISON ===")
    print(f"Baseline R²  : {BASELINE_R2:.4f}  | Tuned R²  : {tuned_r2_mean:.4f}")
    print(f"Baseline RMSE: {BASELINE_RMSE:.4f}  | Tuned RMSE: {cv_rmse_tuned:.4f}")
    
    improvement = tuned_r2_mean - BASELINE_R2
    if improvement > 0.01:
        print(f"\nResult: MEANINGFUL IMPROVEMENT (+{improvement:.4f} R²). The tuned model generalizes better.")
    elif improvement > 0:
        print(f"\nResult: MARGINAL IMPROVEMENT (+{improvement:.4f} R²). The tuning found slightly better parameters, but the baseline was already near optimal.")
    else:
        print(f"\nResult: NO IMPROVEMENT. The tuned model R² ({tuned_r2_mean:.4f}) is worse or equal to the baseline ({BASELINE_R2:.4f}). This is a valid, honest finding that indicates the untuned baseline was already robust for this dataset.")

    # ── STEP 3: Visualizations ──
    print("\nGenerating Optuna Visualizations...")
    
    # Optimization History
    fig_hist = vis.plot_optimization_history(study)
    hist_path = os.path.join(VIS_DIR, 'optuna_optimization_history.png')
    fig_hist.write_image(hist_path, scale=2)
    print(f"  Saved optimization history to {hist_path}")
    
    # Parameter Importance
    fig_param = vis.plot_param_importances(study)
    param_path = os.path.join(VIS_DIR, 'optuna_param_importance.png')
    fig_param.write_image(param_path, scale=2)
    print(f"  Saved param importance to {param_path}")
    
    # ── STEP 4: Update Downstream Outputs ──
    print("\nSaving Tuned Model...")
    tuned_model.fit(X, y)
    model_path = os.path.join(MODEL_DIR, 'xgb_latent_demand.pkl')
    joblib.dump(tuned_model, model_path)
    print(f"✅ Tuned model saved to {model_path} (Replaced untuned model)")
    
    print("\nRe-running Downstream Processes with Tuned Model...")
    
    # 1. Latent Demand Gap
    print("  -> Re-running 11b_latent_demand_gap.py...")
    subprocess.run(["python3", os.path.join(BASE_DIR, 'code', '11b_latent_demand_gap.py')], check=True)
    
    # 2. SHAP Explainability
    print("  -> Re-running 12_shap_explainability.py...")
    subprocess.run(["python3", os.path.join(BASE_DIR, 'code', '12_shap_explainability.py')], check=True)
    
    print("\n" + "="*60)
    print("  ALL STEPS COMPLETE")
    print("="*60)
    print(f"Final Tuned R²: {tuned_r2_mean:.4f} vs Baseline R²: {BASELINE_R2:.4f}")
    print("Regenerated Files:")
    print(" - outputs/models/xgb_latent_demand.pkl")
    print(" - outputs/latent_demand_gap_v2.csv")
    print(" - outputs/shap_values.csv")
    print(" - outputs/shap_explanations.csv")
    print(" - outputs/shap_summary_plot.png")

if __name__ == "__main__":
    main()
