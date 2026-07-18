"""
11c_model_validation.py

Validates the XGBoost model choice against Linear Regression and Random Forest
using 5-fold cross-validation. Compares R², RMSE, and feature importances.
"""

import pandas as pd
import numpy as np
import os
import xgboost as xgb
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR  = os.path.join(BASE_DIR, 'outputs')

def main():
    print("=" * 60)
    print("  MODEL VALIDATION & COMPARISON (5-Fold CV)")
    print("=" * 60)

    # ── Load & Prepare Data (identical to 11b) ──
    df = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))

    scaler = MinMaxScaler()
    target_components = [
        'chronic_diabetes_prevalence',
        'chronic_hypertension_prevalence',
        'macro_population',
    ]
    scaled_targets = scaler.fit_transform(df[target_components])
    y = scaled_targets.sum(axis=1)

    features = [
        'macro_nightlights_mean',
        'macro_economic_employees',
        'macro_literacy_rate',
        'macro_population',
        'macro_economic_establishments',
    ]
    X = df[features]

    # ── Define Models ──
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(
            n_estimators=100, max_depth=4, random_state=42
        ),
        'XGBoost': xgb.XGBRegressor(
            n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42
        ),
    }

    # ── 5-Fold Cross-Validation ──
    results = []
    for name, model in models.items():
        r2_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        # Also get cross-validated predictions for RMSE
        y_pred_cv = cross_val_predict(model, X, y, cv=5)
        rmse = np.sqrt(mean_squared_error(y, y_pred_cv))

        results.append({
            'Model': name,
            'Mean_R2': r2_scores.mean(),
            'Std_R2': r2_scores.std(),
            'RMSE': rmse,
        })

    results_df = pd.DataFrame(results)

    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│  MODEL COMPARISON TABLE (5-Fold Cross-Validation)      │")
    print("├───────────────────┬──────────┬──────────┬──────────────┤")
    print("│ Model             │ Mean R²  │ Std Dev  │ RMSE         │")
    print("├───────────────────┼──────────┼──────────┼──────────────┤")
    for _, row in results_df.iterrows():
        print(
            f"│ {row['Model']:<17s} │ {row['Mean_R2']:>8.4f} │ {row['Std_R2']:>8.4f} │ {row['RMSE']:>12.4f} │"
        )
    print("└───────────────────┴──────────┴──────────┴──────────────┘")

    # ── Feature Importance Comparison ──
    # Retrain RF and XGB on full data for importance extraction
    rf = models['Random Forest'].fit(X, y)
    xgb_model = models['XGBoost'].fit(X, y)

    rf_imp = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
    xgb_imp = pd.Series(xgb_model.feature_importances_, index=features).sort_values(ascending=False)

    print("\n┌──────────────────────────────────────────────────────────────────┐")
    print("│  FEATURE IMPORTANCE RANKING COMPARISON                         │")
    print("├────┬──────────────────────────────┬────────────────────────────-┤")
    print("│ #  │ Random Forest                │ XGBoost                     │")
    print("├────┼──────────────────────────────┼─────────────────────────────┤")
    for rank, (rf_feat, xgb_feat) in enumerate(
        zip(rf_imp.index, xgb_imp.index), 1
    ):
        rf_val = rf_imp[rf_feat]
        xgb_val = xgb_imp[xgb_feat]
        print(
            f"│ {rank}  │ {rf_feat:<20s} ({rf_val:.3f}) │ {xgb_feat:<20s} ({xgb_val:.3f}) │"
        )
    print("└────┴──────────────────────────────┴─────────────────────────────┘")

    # Check agreement
    rf_top = rf_imp.index[0]
    xgb_top = xgb_imp.index[0]
    if rf_top == xgb_top:
        print(f"\n✅ Both models agree: '{rf_top}' is the most important feature.")
    else:
        print(f"\n⚠️  Models disagree on top feature: RF says '{rf_top}', XGBoost says '{xgb_top}'.")

    # Rank correlation (Spearman)
    rf_ranks = rf_imp.rank(ascending=False)
    xgb_ranks = xgb_imp.rank(ascending=False)
    common = rf_ranks.index
    rank_corr = rf_ranks[common].corr(xgb_ranks[common], method='spearman')
    print(f"   Spearman rank correlation of feature importances: {rank_corr:.3f}")

    # ── Save ──
    # Add importance columns to results for the CSV
    imp_df = pd.DataFrame({
        'Feature': features,
        'RF_Importance': [rf_imp[f] for f in features],
        'RF_Rank': [int(rf_ranks[f]) for f in features],
        'XGB_Importance': [xgb_imp[f] for f in features],
        'XGB_Rank': [int(xgb_ranks[f]) for f in features],
    }).sort_values('XGB_Rank')

    out_path = os.path.join(OUT_DIR, 'model_validation_comparison.csv')
    with open(out_path, 'w') as f:
        f.write("# Model Performance (5-Fold CV)\n")
        results_df.to_csv(f, index=False)
        f.write("\n# Feature Importance Comparison\n")
        imp_df.to_csv(f, index=False)

    print(f"\n✅ Saved to {out_path}")


if __name__ == '__main__':
    main()
