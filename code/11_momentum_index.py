"""
11_momentum_index.py

Calculates health, economic, and climate momentum for each district.
Combines them into a final Momentum Score and classifies districts 
into investment quadrants.
"""

import pandas as pd
import numpy as np
import os

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs')

def main():
    print("="*60)
    print("  COMPUTING MOMENTUM INDEX & QUADRANTS")
    print("="*60)
    
    # ── 1. Health Momentum ──
    health = pd.read_csv(os.path.join(PROC_DIR, 'health_master_v2.csv'))
    
    health['nfhs5_diab'] = health[['nfhs5_diabetes_women', 'nfhs5_diabetes_men']].mean(axis=1)
    health['nfhs6_diab'] = health[['nfhs6_diabetes_women', 'nfhs6_diabetes_men']].mean(axis=1)
    health['nfhs5_hyp'] = health[['nfhs5_hypertension_women', 'nfhs5_hypertension_men']].mean(axis=1)
    health['nfhs6_hyp'] = health[['nfhs6_hypertension_women', 'nfhs6_hypertension_men']].mean(axis=1)

    state_nfhs5_diab = health.groupby('state_name')['nfhs5_diab'].transform('mean')
    state_nfhs5_hyp = health.groupby('state_name')['nfhs5_hyp'].transform('mean')

    health['nfhs5_diab_base'] = health['nfhs5_diab'].fillna(state_nfhs5_diab)
    health['nfhs5_hyp_base'] = health['nfhs5_hyp'].fillna(state_nfhs5_hyp)

    health['diab_momentum'] = health['nfhs6_diab'] - health['nfhs5_diab_base']
    health['hyp_momentum'] = health['nfhs6_hyp'] - health['nfhs5_hyp_base']

    health['health_momentum'] = health[['diab_momentum', 'hyp_momentum']].mean(axis=1)
    health['health_momentum_low_conf'] = health['nfhs5_diab'].isna() | health['nfhs5_hyp'].isna()
    
    hm = health[['state_name', 'district_name', 'health_momentum', 'health_momentum_low_conf']]
    
    # ── 2. Economic Momentum ──
    viirs_path = os.path.join(BASE_DIR, 'raw_data', '02_population_economy', 'viirs_annual_pc11dist.csv')
    viirs = pd.read_csv(viirs_path)
    viirs = viirs[viirs['category'] == 'median-masked']
    
    v18 = viirs[viirs['year'] == 2018][['pc11_district_id', 'viirs_annual_mean']].rename(columns={'viirs_annual_mean': 'viirs_2018'})
    v22 = viirs[viirs['year'] == 2022][['pc11_district_id', 'viirs_annual_mean']].rename(columns={'viirs_annual_mean': 'viirs_2022'})
    
    v_growth = v18.merge(v22, on='pc11_district_id', how='inner')
    v_growth['economic_momentum'] = (v_growth['viirs_2022'] - v_growth['viirs_2018']) / (v_growth['viirs_2018'] + 1e-5) * 100
    
    geo = pd.read_csv(os.path.join(PROC_DIR, 'geography_master.csv'))[['pc11_district_id', 'state_name', 'district_name']]
    em = geo.merge(v_growth, on='pc11_district_id', how='left')
    em = em[['state_name', 'district_name', 'economic_momentum']]
    
    # ── 3. Climate Momentum ──
    imputed = pd.read_csv(os.path.join(PROC_DIR, 'master_table_imputed.csv'))
    cm = imputed[['state_name', 'district_name', 'climate_rainfall_deviation_pct']].copy()
    cm = cm.rename(columns={'climate_rainfall_deviation_pct': 'climate_momentum'})
    
    # ── 4. Combine & Rank ──
    indices = pd.read_csv(os.path.join(OUT_DIR, 'final_indices.csv'))
    
    df = indices.merge(hm, on=['state_name', 'district_name'], how='left')
    df = df.merge(em, on=['state_name', 'district_name'], how='left')
    df = df.merge(cm, on=['state_name', 'district_name'], how='left')
    
    # Impute any missing momentum with median so ranking doesn't fail
    for col in ['health_momentum', 'economic_momentum', 'climate_momentum']:
        df[col] = df[col].fillna(df[col].median())
        
    df['rank_health'] = df['health_momentum'].rank(pct=True) * 100
    df['rank_econ'] = df['economic_momentum'].rank(pct=True) * 100
    df['rank_climate'] = df['climate_momentum'].rank(pct=True) * 100
    
    df['Momentum_Score'] = (df['rank_health'] + df['rank_econ'] + df['rank_climate']) / 3.0
    
    # ── 5. Quadrant Classification ──
    mai_median = df['Overall_MAI'].median()
    mom_median = df['Momentum_Score'].median()
    
    def get_quadrant(row):
        mai_high = row['Overall_MAI'] >= mai_median
        mom_high = row['Momentum_Score'] >= mom_median
        if mai_high and mom_high:
            return 'Invest Now'
        elif mai_high and not mom_high:
            return 'Harvest'
        elif not mai_high and mom_high:
            return 'Emerging'
        else:
            return 'Watch'
            
    df['Quadrant'] = df.apply(get_quadrant, axis=1)
    
    out_path = os.path.join(OUT_DIR, 'momentum_and_quadrants.csv')
    df.to_csv(out_path, index=False)
    
    print("\nQuadrant Distribution:")
    print(df['Quadrant'].value_counts().to_string())
    
    print("\n🚀 TOP 10 'EMERGING' DISTRICTS (High Momentum, Low Current Scale)")
    emerging = df[df['Quadrant'] == 'Emerging'].sort_values('Momentum_Score', ascending=False).head(10)
    for i, r in enumerate(emerging.itertuples(), 1):
        print(f"  {i}. {r.district_name} ({r.state_name}) | Momentum: {r.Momentum_Score:.1f} | MAI: {r.Overall_MAI:.1f}")
        
    print(f"\n✅ Saved final output to {out_path}")

if __name__ == '__main__':
    main()
