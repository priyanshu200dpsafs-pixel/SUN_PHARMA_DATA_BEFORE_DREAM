"""
15_statistical_tests.py

Performs rigorous statistical testing on MAI, Quadrants, and Latent Demand Gap.
1. Shapiro-Wilk (Normality)
2. Kruskal-Wallis H-test (Quadrant differences)
3. Pairwise Mann-Whitney U (with Bonferroni correction)
4. Mann-Whitney U for Latent Demand Gap (Top 20 vs Random 20)
"""

import pandas as pd
import numpy as np
import os
from scipy import stats
from itertools import combinations

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')

def main():
    print("="*60)
    print("  STATISTICAL TESTING SUITE")
    print("="*60)
    
    # ── 0. Load Data ──
    momentum_df = pd.read_csv(os.path.join(OUT_DIR, 'momentum_and_quadrants.csv'))
    indices_df = pd.read_csv(os.path.join(OUT_DIR, 'final_indices.csv'))
    gap_df = pd.read_csv(os.path.join(OUT_DIR, 'latent_demand_gap_v2.csv'))
    
    # Merge Overall_MAI if it's not in momentum_df
    if 'Overall_MAI' not in momentum_df.columns:
        df = momentum_df.merge(indices_df[['state_name', 'district_name', 'Overall_MAI']], on=['state_name', 'district_name'], how='left')
    else:
        df = momentum_df
        
    df = df.dropna(subset=['Overall_MAI', 'Quadrant'])
    summary_results = []
    
    # ── STEP 1: Shapiro-Wilk (Normality) ──
    stat_sw, p_sw = stats.shapiro(df['Overall_MAI'])
    is_normal = "Yes" if p_sw > 0.05 else "No (Non-Normal)"
    
    print("\n[STEP 1] Shapiro-Wilk Normality Test on Overall_MAI")
    print(f"  W-Statistic: {stat_sw:.4f}")
    print(f"  p-value:     {p_sw:.4e}")
    print(f"  Result:      {is_normal}")
    
    summary_results.append({
        'Test': 'Shapiro-Wilk (Normality)',
        'Comparison': 'Overall_MAI vs Normal Dist',
        'Statistic': stat_sw,
        'p-value': p_sw,
        'Significant': 'Yes' if p_sw < 0.05 else 'No'
    })
    
    # ── STEP 2: Kruskal-Wallis H-Test ──
    quadrants = df['Quadrant'].unique()
    quadrant_groups = [df[df['Quadrant'] == q]['Overall_MAI'].values for q in quadrants]
    
    stat_kw, p_kw = stats.kruskal(*quadrant_groups)
    
    print("\n[STEP 2] Kruskal-Wallis H-Test (Overall_MAI across 4 Quadrants)")
    print(f"  H-Statistic: {stat_kw:.4f}")
    print(f"  p-value:     {p_kw:.4e}")
    print(f"  Significant: {'Yes' if p_kw < 0.05 else 'No'}")
    
    summary_results.append({
        'Test': 'Kruskal-Wallis',
        'Comparison': 'Overall_MAI across Quadrants',
        'Statistic': stat_kw,
        'p-value': p_kw,
        'Significant': 'Yes' if p_kw < 0.05 else 'No'
    })
    
    # ── STEP 3: Pairwise Mann-Whitney U Tests (with Bonferroni) ──
    if p_kw < 0.05:
        print("\n[STEP 3] Pairwise Mann-Whitney U Tests")
        pairs = list(combinations(quadrants, 2))
        alpha = 0.05
        bonferroni_threshold = alpha / len(pairs)
        
        print(f"  Bonferroni-corrected significance threshold: {bonferroni_threshold:.5f} (0.05 / {len(pairs)})")
        
        for q1, q2 in pairs:
            group1 = df[df['Quadrant'] == q1]['Overall_MAI'].values
            group2 = df[df['Quadrant'] == q2]['Overall_MAI'].values
            
            stat_mw, p_mw = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            survives = "Yes" if p_mw < bonferroni_threshold else "No"
            
            print(f"  - {q1} vs {q2}:")
            print(f"      U: {stat_mw:.1f}, p: {p_mw:.4e} -> Survives Bonferroni? {survives}")
            
            summary_results.append({
                'Test': 'Mann-Whitney U',
                'Comparison': f'{q1} vs {q2}',
                'Statistic': stat_mw,
                'p-value': p_mw,
                'Significant': survives
            })
    else:
        print("\n[STEP 3] Skipped pairwise tests because Kruskal-Wallis was not significant.")
        
    # ── STEP 4: Latent Demand Gap (Top 20 vs Random 20) ──
    print("\n[STEP 4] Mann-Whitney U (Latent Demand Gap: Top 20 vs Random 20)")
    
    gap_df = gap_df.dropna(subset=['Latent_Demand_Gap']).sort_values('Latent_Demand_Gap', ascending=False)
    
    # Top 20 
    top_20 = gap_df.head(20)
    
    # Random 20 from the rest
    rest = gap_df.iloc[20:]
    np.random.seed(42) # For reproducibility
    random_20 = rest.sample(n=20)
    
    stat_gap, p_gap = stats.mannwhitneyu(top_20['Latent_Demand_Gap'], random_20['Latent_Demand_Gap'], alternative='two-sided')
    
    print(f"  U-Statistic: {stat_gap:.1f}")
    print(f"  p-value:     {p_gap:.4e}")
    print(f"  Significant: {'Yes' if p_gap < 0.05 else 'No'}")
    
    summary_results.append({
        'Test': 'Mann-Whitney U',
        'Comparison': 'Latent_Demand_Gap (Top 20 vs Random 20)',
        'Statistic': stat_gap,
        'p-value': p_gap,
        'Significant': 'Yes' if p_gap < 0.05 else 'No'
    })
    
    # ── 5. Save Summary Table ──
    summary_df = pd.DataFrame(summary_results)
    out_path = os.path.join(OUT_DIR, 'statistical_tests_summary.csv')
    summary_df.to_csv(out_path, index=False)
    
    print("\n" + "="*60)
    print(f"✅ Saved clean summary table to {out_path}")
    print("="*60)

if __name__ == "__main__":
    main()
