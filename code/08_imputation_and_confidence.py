"""
08_imputation_and_confidence.py

Performs MICE imputation on the curated master table and generates 
data confidence tiers for each district.
"""

import pandas as pd
import numpy as np
import os
import random
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')

def main():
    print("="*60)
    print("  MICE IMPUTATION & CONFIDENCE FLAGGING")
    print("="*60)
    
    in_path = os.path.join(PROC_DIR, 'master_table_selected.csv')
    df = pd.read_csv(in_path)
    
    # Isolate numeric columns for imputation (excluding data_completeness_score if present)
    non_impute_cols = ['state_name', 'district_name', 'chronic_diabetes_source', 'chronic_hypertension_source', 'data_completeness_score']
    impute_cols = [c for c in df.columns if c not in non_impute_cols]
    
    print(f"Columns to impute: {len(impute_cols)}")
    
    # Step 1: Create boolean "was_imputed" flags for missing values
    imputed_flags_created = 0
    for col in impute_cols:
        if df[col].isnull().any():
            df[f'{col}_was_imputed'] = df[col].isnull()
            imputed_flags_created += 1
            
    print(f"Created 'was_imputed' flags for {imputed_flags_created} columns.")
    
    # Set up bounds for IterativeImputer
    # We will enforce logical boundaries (e.g. >= 0 for population/hospitals, 0-100 for rates)
    min_vals = []
    max_vals = []
    for col in impute_cols:
        if 'literacy' in col or 'prevalence' in col:
            min_vals.append(0)
            max_vals.append(100)
        elif 'deviation_pct' in col:
            min_vals.append(-100)
            max_vals.append(np.inf)
        else:
            min_vals.append(0)
            max_vals.append(np.inf)
            
    # Perform Imputation
    imputer = IterativeImputer(
        min_value=min_vals, 
        max_value=max_vals, 
        random_state=42, 
        max_iter=20
    )
    
    df_imputed = df.copy()
    imputed_data = imputer.fit_transform(df[impute_cols])
    
    # Put imputed values back
    for i, col in enumerate(impute_cols):
        df_imputed[col] = imputed_data[:, i]
        
    # Tally how many values were imputed per column
    print("\nValues Imputed per Column:")
    for col in impute_cols:
        if f'{col}_was_imputed' in df_imputed.columns:
            imputed_count = df_imputed[f'{col}_was_imputed'].sum()
            print(f"  {col}: {imputed_count}")
            
    # Step 2: Data Confidence Flag
    # Calculate % of the 14 core variables that were imputed for each district
    # We only count the 'impute_cols' which is exactly 14 variables in this script
    impute_flag_cols = [f'{col}_was_imputed' for col in impute_cols if f'{col}_was_imputed' in df_imputed.columns]
    
    df_imputed['imputed_feature_count'] = df_imputed[impute_flag_cols].sum(axis=1)
    df_imputed['imputed_pct'] = (df_imputed['imputed_feature_count'] / len(impute_cols)) * 100
    
    def assign_confidence(pct):
        if pct <= 10:
            return 'HIGH'
        elif pct <= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    df_imputed['data_confidence_tier'] = df_imputed['imputed_pct'].apply(assign_confidence)
    
    print("\nData Confidence Distribution:")
    print(df_imputed['data_confidence_tier'].value_counts().to_string())
    
    # Step 3: Sanity Check 
    print("\n" + "="*40)
    print(" SANITY CHECK: Original vs Imputed (10 random districts)")
    print("="*40)
    
    # Pick 10 random districts that had AT LEAST one imputed value
    districts_with_imputation = df_imputed[df_imputed['imputed_feature_count'] > 0]
    if len(districts_with_imputation) >= 10:
        sample = districts_with_imputation.sample(10, random_state=42)
    else:
        sample = districts_with_imputation
        
    for idx, row in sample.iterrows():
        print(f"\n[{row['state_name']} - {row['district_name']}]")
        for col in impute_cols:
            flag_col = f'{col}_was_imputed'
            if flag_col in df_imputed.columns and row[flag_col]:
                orig_val = df.at[idx, col]
                imp_val = row[col]
                print(f"  {col}: {orig_val} -> {imp_val:.2f}")
                # Simple bounds check warning
                if imp_val < 0 and 'deviation' not in col:
                    print(f"    ⚠️ WARNING: Implausible negative value!")
                if ('prevalence' in col or 'literacy' in col) and imp_val > 100:
                    print(f"    ⚠️ WARNING: Implausible percentage > 100%!")
                    
    out_path = os.path.join(PROC_DIR, 'master_table_imputed.csv')
    df_imputed.to_csv(out_path, index=False)
    print(f"\n✅ Saved to {out_path}")

if __name__ == '__main__':
    main()
