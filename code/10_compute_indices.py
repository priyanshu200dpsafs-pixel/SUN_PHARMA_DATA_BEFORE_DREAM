"""
10_compute_indices.py

Calculates the Acute, Chronic, and Overall Market Attractiveness Indices (MAI),
applying hierarchical shrinkage to low-confidence districts, and rescales 
the final outputs.
"""

import pandas as pd
import numpy as np
import os

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def main():
    print("="*60)
    print("  COMPUTING FINAL MARKET ATTRACTIVENESS INDICES")
    print("="*60)
    
    scores_path = os.path.join(PROC_DIR, 'normalized_scores.csv')
    weights_path = os.path.join(PROC_DIR, 'weights_table.csv')
    
    df_scores = pd.read_csv(scores_path)
    df_weights = pd.read_csv(weights_path)
    
    # Create a dictionary of original entropy weights
    entropy_dict = pd.Series(df_weights.Entropy_Weight.values, index=df_weights.Variable).to_dict()
    # Create a dictionary of overall blended weights
    overall_blended_dict = pd.Series(df_weights.Blended_Weight.values, index=df_weights.Variable).to_dict()
    
    # ── STEP 1: Three Separate Weight Profiles ──
    
    # ACUTE INDEX
    acute_high = [
        'infra_hospitals_count', 'infra_phc_chc_count', 'infra_pmbjp_kendra_count',
        'climate_rainfall_volatility', 'climate_rainfall_deviation_pct'
    ]
    acute_med = [
        'macro_population', 'macro_nightlights_mean'
    ]
    acute_vars = acute_high + acute_med
    
    acute_ahp_total = (len(acute_high) * 3) + (len(acute_med) * 1)
    acute_ahp = {v: (3.0 / acute_ahp_total if v in acute_high else 1.0 / acute_ahp_total) for v in acute_vars}
    
    acute_entropy_total = sum(entropy_dict[v] for v in acute_vars)
    acute_weights = {}
    for v in acute_vars:
        norm_entropy = entropy_dict[v] / acute_entropy_total
        acute_weights[v] = 0.5 * norm_entropy + 0.5 * acute_ahp[v]
        
    # CHRONIC INDEX
    chronic_high = [
        'chronic_diabetes_prevalence', 'chronic_hypertension_prevalence', 'chronic_cancer_incidence_aar',
        'macro_nightlights_mean', 'macro_economic_employees', 'macro_literacy_rate'
    ]
    chronic_med = [
        'infra_pmbjp_kendra_count'
    ]
    chronic_vars = chronic_high + chronic_med
    
    chronic_ahp_total = (len(chronic_high) * 3) + (len(chronic_med) * 1)
    chronic_ahp = {v: (3.0 / chronic_ahp_total if v in chronic_high else 1.0 / chronic_ahp_total) for v in chronic_vars}
    
    chronic_entropy_total = sum(entropy_dict[v] for v in chronic_vars)
    chronic_weights = {}
    for v in chronic_vars:
        norm_entropy = entropy_dict[v] / chronic_entropy_total
        chronic_weights[v] = 0.5 * norm_entropy + 0.5 * chronic_ahp[v]
        
    # OVERALL INDEX
    overall_vars = list(overall_blended_dict.keys())
    overall_weights = overall_blended_dict
    
    # ── STEP 2: Compute Raw Composite Scores ──
    
    df_res = pd.DataFrame()
    df_res['state_name'] = df_scores['state_name']
    df_res['district_name'] = df_scores['district_name']
    df_res['confidence_tier'] = df_scores['data_confidence_tier']
    
    def compute_score(row, weights):
        score = 0.0
        for v, w in weights.items():
            score += row[v] * w
        return score
        
    df_res['raw_acute'] = df_scores.apply(lambda row: compute_score(row, acute_weights), axis=1)
    df_res['raw_chronic'] = df_scores.apply(lambda row: compute_score(row, chronic_weights), axis=1)
    df_res['raw_overall'] = df_scores.apply(lambda row: compute_score(row, overall_weights), axis=1)
    
    # ── STEP 3: Hierarchical Shrinkage ──
    
    shrink_map = {'HIGH': 0.0, 'MEDIUM': 0.25, 'LOW': 0.50}
    df_res['shrink_pct'] = df_res['confidence_tier'].map(shrink_map)
    
    for idx_name in ['acute', 'chronic', 'overall']:
        raw_col = f'raw_{idx_name}'
        state_mean = df_res.groupby('state_name')[raw_col].transform('mean')
        
        shrunk_score = (1 - df_res['shrink_pct']) * df_res[raw_col] + (df_res['shrink_pct'] * state_mean)
        df_res[f'shrunk_{idx_name}'] = shrunk_score
        
    # ── STEP 4: Final Output Rescaling ──
    
    def min_max_rescale(series):
        s_min = series.min()
        s_max = series.max()
        return ((series - s_min) / (s_max - s_min)) * 100
        
    df_res['Acute_MAI'] = min_max_rescale(df_res['shrunk_acute'])
    df_res['Chronic_MAI'] = min_max_rescale(df_res['shrunk_chronic'])
    df_res['Overall_MAI'] = min_max_rescale(df_res['shrunk_overall'])
    
    # Rank (1 = highest score)
    df_res['Rank_Acute'] = df_res['Acute_MAI'].rank(ascending=False, method='min').astype(int)
    df_res['Rank_Chronic'] = df_res['Chronic_MAI'].rank(ascending=False, method='min').astype(int)
    df_res['Rank_Overall'] = df_res['Overall_MAI'].rank(ascending=False, method='min').astype(int)
    
    final_cols = [
        'district_name', 'state_name', 'confidence_tier',
        'Overall_MAI', 'Rank_Overall',
        'Chronic_MAI', 'Rank_Chronic',
        'Acute_MAI', 'Rank_Acute'
    ]
    df_final = df_res[final_cols].copy()
    
    out_path = os.path.join(OUT_DIR, 'final_indices.csv')
    df_final.to_csv(out_path, index=False)
    
    # Print Top 20 for Sanity Check
    print("\n🏆 TOP 20 DISTRICTS: OVERALL MAI")
    top_overall = df_final.sort_values('Rank_Overall').head(20)
    for i, r in enumerate(top_overall.itertuples(), 1):
        print(f"  {i}. {r.district_name} ({r.state_name}) - Score: {r.Overall_MAI:.1f}")
        
    print("\n🏆 TOP 20 DISTRICTS: CHRONIC MAI")
    top_chronic = df_final.sort_values('Rank_Chronic').head(20)
    for i, r in enumerate(top_chronic.itertuples(), 1):
        print(f"  {i}. {r.district_name} ({r.state_name}) - Score: {r.Chronic_MAI:.1f}")
        
    print("\n🏆 TOP 20 DISTRICTS: ACUTE MAI")
    top_acute = df_final.sort_values('Rank_Acute').head(20)
    for i, r in enumerate(top_acute.itertuples(), 1):
        print(f"  {i}. {r.district_name} ({r.state_name}) - Score: {r.Acute_MAI:.1f}")
        
    print(f"\n✅ Saved to {out_path}")

if __name__ == '__main__':
    main()
