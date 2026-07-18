"""
06_merge_master_table.py

Merges all intermediate master files into the final master_table_v1.csv.
Reports missingness and data completeness scores.
"""

import pandas as pd
import os

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')

def main():
    print("="*60)
    print("  MERGING FINAL MASTER TABLE")
    print("="*60)
    
    # Base contains Geo + Pop + Econ + Health + NCRP
    health_path = os.path.join(PROC_DIR, 'health_master_v2.csv')
    if not os.path.exists(health_path):
        print(f"Error: {health_path} not found.")
        return
    master = pd.read_csv(health_path)
    
    # Climate contains Base + Climate columns
    climate_path = os.path.join(PROC_DIR, 'climate_master.csv')
    if os.path.exists(climate_path):
        climate = pd.read_csv(climate_path)
        climate_cols = [
            'state_name', 'district_name', 
            'csv_annual_rainfall_mm', 'csv_monthly_rainfall_std', 
            'xls_actual_mm', 'xls_normal_mm', 'xls_deviation_pct'
        ]
        # Only keep columns that actually exist in the file just to be safe
        keep_cols = [c for c in climate_cols if c in climate.columns]
        climate = climate[keep_cols]
        master = master.merge(climate, on=['state_name', 'district_name'], how='left')
    
    # PMBJP contains Base + PMBJP columns
    pmbjp_path = os.path.join(PROC_DIR, 'pmbjp_master.csv')
    if os.path.exists(pmbjp_path):
        pmbjp = pd.read_csv(pmbjp_path)
        pmbjp_cols = ['state_name', 'district_name', 'pmbjp_kendra_count']
        keep_cols = [c for c in pmbjp_cols if c in pmbjp.columns]
        pmbjp = pmbjp[keep_cols]
        master = master.merge(pmbjp, on=['state_name', 'district_name'], how='left')
        
    print(f"Final row count: {len(master)}")
    print(f"Final column count: {len(master.columns)}")
    
    missing_pct = (master.isnull().sum() / len(master)) * 100
    missing_pct = missing_pct.sort_values(ascending=False)
    
    print("\nMissing % per column (worst to best):")
    # Print worst 20
    for col, pct in list(missing_pct.items())[:20]:
        print(f"  {col}: {pct:.1f}%")
    print(f"  ... and {len(missing_pct)-20} more columns.")
        
    # Calculate completeness score
    # Count of non-null fields divided by total fields
    master['data_completeness_score'] = (master.notnull().sum(axis=1) / len(master.columns)) * 100
    
    out_path = os.path.join(PROC_DIR, 'master_table_v1.csv')
    master.to_csv(out_path, index=False)
    
    print(f"\n✅ Saved to {out_path}")

if __name__ == '__main__':
    main()
