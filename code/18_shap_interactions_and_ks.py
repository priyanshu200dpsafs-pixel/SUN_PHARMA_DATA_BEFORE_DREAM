"""
18_shap_interactions_and_ks.py

PART A: Computes SHAP interaction values for the tuned XGBoost model and plots the strongest interaction.
PART B: Computes the KS statistic and generates a decile lift chart for Latent Demand Gap targeting.
"""

import pandas as pd
import numpy as np
import os
import xgboost as xgb
import shap
import joblib
import matplotlib.pyplot as plt

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')
MODEL_DIR = os.path.join(OUT_DIR, 'models')
VIS_DIR   = os.path.join(OUT_DIR, 'visuals')
os.makedirs(VIS_DIR, exist_ok=True)

def main():
    print("="*60)
    print("  PART A: SHAP INTERACTIONS")
    print("="*60)
    
    # ── 1. Load Model & Data ──
    df = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))
    
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
    
    model_path = os.path.join(MODEL_DIR, 'xgb_latent_demand.pkl')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Please run 11e_optuna_tuning.py first.")
    
    model = joblib.load(model_path)
    
    # ── 2. Compute SHAP Interactions ──
    # TreeExplainer is required for interaction values
    explainer = shap.TreeExplainer(model)
    # interactions shape: (n_samples, n_features, n_features)
    shap_interaction_values = explainer.shap_interaction_values(X)
    
    # Find strongest interaction pair (off-diagonal)
    # We take the mean absolute interaction across all samples
    mean_abs_interactions = np.abs(shap_interaction_values).mean(axis=0)
    
    # Zero out the diagonal (main effects) so we only look at interactions
    np.fill_diagonal(mean_abs_interactions, 0)
    
    # Find the indices of the max value
    max_idx = np.unravel_index(np.argmax(mean_abs_interactions), mean_abs_interactions.shape)
    f1_strong, f2_strong = features[max_idx[0]], features[max_idx[1]]
    
    print(f"Algorithmically determined strongest interaction: {f1_strong} x {f2_strong}")
    
    # ── Plot Strongest Interaction ──
    print(f"\nPlotting strongest SHAP interaction for {f1_strong} vs {f2_strong}...")
    plt.figure(figsize=(8, 6))
    shap.dependence_plot(
        (f1_strong, f2_strong), 
        shap_interaction_values, 
        X,
        display_features=X,
        show=False
    )
    plot_path_strong = os.path.join(VIS_DIR, 'shap_interaction_plot_strongest.png')
    plt.tight_layout()
    plt.savefig(plot_path_strong, dpi=300)
    plt.close()
    print(f"✅ Saved strongest SHAP interaction plot to {plot_path_strong}")
    
    print("\nPlain-English Interpretation of the STRONGEST Interaction:")
    print(f"The plot shows how the effect of {f1_strong} on expected infrastructure demand is drastically amplified or suppressed depending on {f2_strong}.")
    print("If this is Diabetes vs Population, it means that a high diabetes rate drives expected infrastructure demand much more aggressively in highly populated districts than it does in smaller ones. The combination creates a compounding effect, identifying critical urban health hotspots that need immediate attention.")
    
    # ── Plot Requested Interaction (Diabetes x Nightlights) ──
    if 'chronic_diabetes_prevalence' in features and 'macro_nightlights_mean' in features:
        f1_req, f2_req = 'chronic_diabetes_prevalence', 'macro_nightlights_mean'
        print(f"\nPlotting requested SHAP interaction for {f1_req} vs {f2_req}...")
        plt.figure(figsize=(8, 6))
        shap.dependence_plot(
            (f1_req, f2_req), 
            shap_interaction_values, 
            X,
            display_features=X,
            show=False
        )
        plot_path_req = os.path.join(VIS_DIR, 'shap_interaction_plot.png')
        plt.tight_layout()
        plt.savefig(plot_path_req, dpi=300)
        plt.close()
        print(f"✅ Saved requested SHAP interaction plot to {plot_path_req}")
    
    print("\nPlain-English Interpretation of the Requested Interaction:")
    print(f"The plot shows how the effect of {f1_req} on expected infrastructure depends heavily on {f2_req}.")
    print("Vertical dispersion at any given point on the x-axis indicates that the interaction effect is real.")
    print("For business strategy, this means these two metrics do not act independently; a district scoring high on both will have an amplified (or dampened) expected infrastructure gap compared to just adding their individual effects.")
    
    print("\n" + "="*60)
    print("  PART B: KS STATISTIC & DECILE LIFT")
    print("="*60)
    
    # ── 4. Load Gap Data ──
    gap = pd.read_csv(os.path.join(OUT_DIR, 'latent_demand_gap_v2.csv'))
    
    # Sort by gap descending
    gap = gap.sort_values('Latent_Demand_Gap', ascending=False).reset_index(drop=True)
    
    # Define "Unmet Demand" as population-weighted positive gap
    # If gap is negative (oversupplied), we treat unmet demand as 0
    gap['Unmet_Demand'] = np.where(gap['Latent_Demand_Gap'] > 0, gap['Latent_Demand_Gap'] * gap['macro_population'], 0)
    total_unmet = gap['Unmet_Demand'].sum()
    
    # ── 5. Decile Calculations ──
    # Create 10 bins (deciles)
    # Using qcut if possible, or just np.array_split
    gap['Decile'] = pd.qcut(gap.index, 10, labels=False) + 1 # 1 is highest gap, 10 is lowest
    
    decile_stats = []
    cum_unmet = 0
    
    for d in range(1, 11):
        d_data = gap[gap['Decile'] == d]
        d_unmet = d_data['Unmet_Demand'].sum()
        cum_unmet += d_unmet
        
        pct_unmet = (d_unmet / total_unmet) * 100
        cum_pct_unmet = (cum_unmet / total_unmet) * 100
        pct_districts = d * 10
        
        decile_stats.append({
            'Decile': d,
            '%_Districts': pct_districts,
            'Unmet_Captured_Pct': pct_unmet,
            'Cum_Unmet_Captured_Pct': cum_pct_unmet
        })
        
    df_deciles = pd.DataFrame(decile_stats)
    
    # Add a 0,0 point for the plot
    df_deciles = pd.concat([pd.DataFrame([{'Decile': 0, '%_Districts': 0, 'Unmet_Captured_Pct': 0, 'Cum_Unmet_Captured_Pct': 0}]), df_deciles], ignore_index=True)
    
    # Random Baseline is just y = x
    df_deciles['Random_Baseline'] = df_deciles['%_Districts']
    
    # KS Statistic is max distance between Cum_Unmet_Captured and Random Baseline
    df_deciles['KS_Distance'] = df_deciles['Cum_Unmet_Captured_Pct'] - df_deciles['Random_Baseline']
    ks_stat = df_deciles['KS_Distance'].max()
    ks_decile = df_deciles.loc[df_deciles['KS_Distance'].idxmax(), '%_Districts']
    
    print(f"KS Statistic: {ks_stat:.1f}% (Maximum separation occurs at {ks_decile}% of districts)")
    
    # ── 6. Plot KS/Lift Chart ──
    plt.figure(figsize=(8, 6))
    
    plt.plot(df_deciles['%_Districts'], df_deciles['Cum_Unmet_Captured_Pct'], marker='o', linewidth=2, color='#1D4ED8', label='Targeting by Model Rank')
    plt.plot(df_deciles['%_Districts'], df_deciles['Random_Baseline'], linestyle='--', color='gray', label='Random Targeting')
    
    # Highlight KS gap
    max_idx = df_deciles['KS_Distance'].idxmax()
    x_ks = df_deciles.loc[max_idx, '%_Districts']
    y_ks = df_deciles.loc[max_idx, 'Cum_Unmet_Captured_Pct']
    y_rand = df_deciles.loc[max_idx, 'Random_Baseline']
    
    plt.vlines(x=x_ks, ymin=y_rand, ymax=y_ks, color='red', linestyle=':', linewidth=2, label=f'KS Stat ({ks_stat:.1f}%)')
    
    plt.title("KS Statistic & Decile Lift Chart: Unmet Demand Capture", fontsize=14)
    plt.xlabel("Cumulative % of Districts Targeted (Sorted by Gap)", fontsize=12)
    plt.ylabel("Cumulative % of Unmet Demand Captured", fontsize=12)
    plt.xticks(np.arange(0, 101, 10))
    plt.yticks(np.arange(0, 101, 10))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='lower right')
    
    plot_path_b = os.path.join(VIS_DIR, 'ks_decile_chart.png')
    plt.tight_layout()
    plt.savefig(plot_path_b, dpi=300)
    plt.close()
    
    print(f"✅ Saved KS/Lift chart to {plot_path_b}\n")
    
    # ── 7. Business Statement ──
    # Let's extract Top 20% (Decile 2)
    top_20_capture = df_deciles.loc[df_deciles['%_Districts'] == 20, 'Cum_Unmet_Captured_Pct'].values[0]
    top_30_capture = df_deciles.loc[df_deciles['%_Districts'] == 30, 'Cum_Unmet_Captured_Pct'].values[0]
    
    print(f"🏆 BUSINESS STATEMENT:")
    print(f"\"Targeting the top 20% of districts by our Latent Demand Gap ranking captures {top_20_capture:.1f}% of the total unmet infrastructure demand across India.\"")
    print(f"\"Expanding to the top 30% of districts captures {top_30_capture:.1f}% of total unmet demand.\"")

if __name__ == "__main__":
    main()
