"""
11d_fix_latent_demand_target.py

Experiments with alternative prediction targets:
1. Predicting chronic_diabetes_prevalence directly using economic features.
2. Predicting infrastructure adequacy directly using both economic and health features.
"""

import pandas as pd
import numpy as np
import os
import xgboost as xgb
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR = os.path.join(BASE_DIR, 'processed_data')

def run_cv(X, y, title):
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=4, random_state=42),
        'XGBoost': xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    }
    
    print(f"\n{title}")
    print("-" * 60)
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        print(f"{name:18s} | Mean R²: {scores.mean():>7.4f} | Std Dev: {scores.std():>7.4f}")

def main():
    print("=" * 60)
    print("  MODEL RE-VALIDATION EXPERIMENTS")
    print("=" * 60)

    df = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))

    # Features
    economic_features = [
        'macro_nightlights_mean',
        'macro_economic_employees',
        'macro_literacy_rate',
        'macro_population',
        'macro_economic_establishments'
    ]

    # ── EXPERIMENT 1: Single Target (Diabetes) ──
    print("\n[EXPERIMENT 1] Predicting Diabetes Prevalence using Economic Features")
    X1 = df[economic_features]
    y1 = df['chronic_diabetes_prevalence']
    run_cv(X1, y1, "Predicting Diabetes Prevalence (Raw %)")

    # ── EXPERIMENT 2: Predicting Infrastructure Gap directly ──
    print("\n[EXPERIMENT 2] Predicting Infrastructure Adequacy using Economic + Health Features")
    
    # Target: Infrastructure (Hospitals + PHCs/CHCs)
    df['infra_raw'] = df['infra_hospitals_count'] + df['infra_phc_chc_count']
    y2_pct = df['infra_raw'].rank(pct=True) * 100
    y2_raw = df['infra_raw']

    X2_features = economic_features + ['chronic_diabetes_prevalence', 'chronic_hypertension_prevalence']
    X2 = df[X2_features]
    
    run_cv(X2, y2_pct, "Predicting Infrastructure Adequacy (Percentile Rank)")
    run_cv(X2, y2_raw, "Predicting Infrastructure Adequacy (Raw Facility Count)")

if __name__ == '__main__':
    main()
