"""
09_normalize_and_weight.py

Performs percentile-rank normalization, calculates Entropy weights, assigns 
AHP-based business weights, and blends them for final weighting.
"""

import pandas as pd
import numpy as np
import os

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')

def main():
    print("="*60)
    print("  NORMALIZATION & WEIGHTING")
    print("="*60)
    
    in_path = os.path.join(PROC_DIR, 'master_table_imputed.csv')
    df = pd.read_csv(in_path)
    
    # Isolate the 14 core numeric variables
    prefixes = ['macro_', 'chronic_', 'infra_', 'climate_']
    core_vars = [c for c in df.columns if any(c.startswith(p) for p in prefixes) 
                 and df[c].dtype in ['float64', 'int64'] 
                 and not c.endswith('_was_imputed')]
                 
    # ── STEP 1: Percentile-Rank Normalization ──
    df_norm = df.copy()
    
    # In our specific dataset, for Sun Pharma's prioritization:
    # - Macro: higher population/economy = larger market = BETTER
    # - Chronic: higher prevalence/incidence = higher burden = BETTER target
    # - Infra: higher hospitals/kendras = better distribution channels = BETTER
    # - Climate: higher volatility/deviation = higher acute risk = BETTER target
    # Therefore, we do NOT need to invert any variables. Higher is always better here.
    
    for var in core_vars:
        # pct=True gives values from 0.0 to 1.0, multiply by 100
        df_norm[var] = df_norm[var].rank(pct=True) * 100
        
    print("Percentile Rank Normalization Complete.")
    print("Sample Before/After Distribution:")
    sample_vars = np.random.choice(core_vars, 3, replace=False)
    for var in sample_vars:
        print(f"\n[{var}]")
        print(f"  Before: Min={df[var].min():.2f}, Median={df[var].median():.2f}, Max={df[var].max():.2f}")
        print(f"  After:  Min={df_norm[var].min():.2f}, Median={df_norm[var].median():.2f}, Max={df_norm[var].max():.2f}")
        
    # ── STEP 2: Entropy Weighting (On RAW Data) ──
    # Entropy weighting measures the distributional spread/skew. 
    # Therefore, we calculate it on Min-Max scaled raw data, NOT percentiles.
    epsilon = 1e-6
    n = len(df)
    k = 1.0 / np.log(n)
    
    entropy_weights = {}
    for var in core_vars:
        # Min-Max scale the raw data to [0, 1]
        x = df[var].values
        x_min = x.min()
        x_max = x.max()
        # Avoid division by zero if a variable is perfectly constant
        if x_max == x_min:
            x_scaled = np.zeros_like(x)
        else:
            x_scaled = (x - x_min) / (x_max - x_min)
            
        # Add epsilon to avoid log(0)
        x_scaled = x_scaled + epsilon
        
        # Proportion P_ij
        p = x_scaled / x_scaled.sum()
        
        # Entropy E_j
        e = -k * np.sum(p * np.log(p))
        
        # Divergence d_j
        d = 1.0 - e
        entropy_weights[var] = d
        
    # Normalize weights so they sum to 1.0
    total_d = sum(entropy_weights.values())
    for var in core_vars:
        entropy_weights[var] = entropy_weights[var] / total_d
        
    print("\nEntropy Weights (Data-driven):")
    sorted_entropy = sorted(entropy_weights.items(), key=lambda item: item[1], reverse=True)
    for var, w in sorted_entropy:
        print(f"  {var}: {w:.4f}")
        
    # ── STEP 3: AHP Weights (Business Logic) ──
    # Macro: 25%, Chronic: 30%, Infra: 25%, Climate: 20%
    category_weights = {
        'macro': 0.25,
        'chronic': 0.30,
        'infra': 0.25,
        'climate': 0.20
    }
    
    counts = {'macro': 0, 'chronic': 0, 'infra': 0, 'climate': 0}
    for var in core_vars:
        cat = var.split('_')[0]
        counts[cat] += 1
        
    ahp_weights = {}
    for var in core_vars:
        cat = var.split('_')[0]
        ahp_weights[var] = category_weights[cat] / counts[cat]
        
    print("\nAHP Weights vs Entropy Weights:")
    for var in core_vars:
        print(f"  {var} | AHP: {ahp_weights[var]:.4f} | Entropy: {entropy_weights[var]:.4f}")
        
    # ── STEP 4: Blended Final Weight ──
    # 50/50 blend assumption documented here:
    # Stated Assumption: We equally blend purely objective statistical variance (Entropy)
    # with subjective strategic business logic (AHP) to ensure neither noise nor 
    # human bias overly dominates the final index.
    
    blended_weights = {}
    for var in core_vars:
        blended_weights[var] = 0.5 * entropy_weights[var] + 0.5 * ahp_weights[var]
        
    # Create Weights DataFrame
    weights_df = pd.DataFrame({
        'Variable': core_vars,
        'Entropy_Weight': [entropy_weights[v] for v in core_vars],
        'AHP_Weight': [ahp_weights[v] for v in core_vars],
        'Blended_Weight': [blended_weights[v] for v in core_vars]
    })
    
    # Sort for final output
    weights_df = weights_df.sort_values(by='Blended_Weight', ascending=False)
    
    print("\nFinal Blended Weights (Sorted):")
    for _, row in weights_df.iterrows():
        print(f"  {row['Variable']}: {row['Blended_Weight']:.4f}")
    
    print(f"\nSum of blended weights: {weights_df['Blended_Weight'].sum():.4f}")
    
    # Save files
    weights_path = os.path.join(PROC_DIR, 'weights_table.csv')
    weights_df.to_csv(weights_path, index=False)
    
    scores_path = os.path.join(PROC_DIR, 'normalized_scores.csv')
    # Save the geography keys + normalized variables + confidence flags
    keep_cols = ['state_name', 'district_name', 'data_completeness_score', 'data_confidence_tier'] + core_vars
    df_norm[keep_cols].to_csv(scores_path, index=False)
    
    print(f"\n✅ Saved weights to {weights_path}")
    print(f"✅ Saved normalized scores to {scores_path}")

if __name__ == '__main__':
    main()
