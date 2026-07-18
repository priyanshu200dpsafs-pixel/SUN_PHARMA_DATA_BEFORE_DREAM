"""
05_load_climate_data.py

Loads and processes daily and timeseries climate data, matches districts using
fuzzy logic, and joins onto health_master_v2.csv.
"""

import pandas as pd
import numpy as np
import os
import warnings
from rapidfuzz import fuzz, process

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR  = os.path.join(BASE_DIR, 'raw_data', '06_climate')
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')

def fuzzy_match_states(source_df, master_df, source_name):
    match_log = []
    unmatched = []
    mapping = {}
    
    master_states = set(master_df['state_name'].dropna().unique())
    source_states = set(source_df['state_name'].dropna().unique())
    
    matched_exact = source_states.intersection(master_states)
    unmatched_source = source_states - matched_exact
    unmatched_master = master_states - matched_exact
    
    for state in unmatched_source:
        if not unmatched_master:
            unmatched.append({'source': source_name, 'state': state, 'district': 'N/A (State level)'})
            continue
            
        state_clean = state.replace(' ', '')
        best_match = None
        best_score = 0
        
        for m_state in unmatched_master:
            m_clean = m_state.replace(' ', '')
            score = fuzz.ratio(state_clean, m_clean)
            if score > best_score:
                best_score = score
                best_match = m_state
                
        if best_match and best_score >= 85:
            match_log.append({
                'source': source_name,
                'state': state,
                'source_district': 'STATE LEVEL',
                'master_district': best_match,
                'score': best_score
            })
            mapping[state] = best_match
            unmatched_master.remove(best_match)
        else:
            unmatched.append({'source': source_name, 'state': state, 'district': 'N/A (State level)'})
            
    return mapping, match_log, unmatched

def fuzzy_match_districts(source_df, master_df, source_name):
    match_log = []
    unmatched = []
    mapping = {}
    
    states = source_df['state_name'].dropna().unique()
    for state in states:
        master_state = master_df[master_df['state_name'] == state]
        if master_state.empty:
            for dist in source_df[source_df['state_name'] == state]['district_name'].dropna().unique():
                unmatched.append({'source': source_name, 'state': state, 'district': dist})
            continue
            
        master_dists = set(master_state['district_name'].dropna().unique())
        source_dists = set(source_df[source_df['state_name'] == state]['district_name'].dropna().unique())
        
        matched_exact = source_dists.intersection(master_dists)
        unmatched_source = source_dists - matched_exact
        unmatched_master = master_dists - matched_exact
        
        for dist in unmatched_source:
            if not unmatched_master:
                unmatched.append({'source': source_name, 'state': state, 'district': dist})
                continue
                
            match = process.extractOne(dist, list(unmatched_master), scorer=fuzz.token_sort_ratio, score_cutoff=85)
            if match:
                best_match, score, _ = match
                match_log.append({
                    'source': source_name, 
                    'state': state, 
                    'source_district': dist, 
                    'master_district': best_match, 
                    'score': score
                })
                mapping[(state, dist)] = best_match
                unmatched_master.remove(best_match)
            else:
                unmatched.append({'source': source_name, 'state': state, 'district': dist})
                
    return mapping, match_log, unmatched

def clean_dataframe(df, source_name, master):
    df['state_name'] = df['state_name'].str.upper().str.strip()
    df['district_name'] = df['district_name'].str.upper().str.strip()
    
    state_map, _, _ = fuzzy_match_states(df, master, f'{source_name} (State)')
    df['state_name'] = df['state_name'].replace(state_map)
    
    dist_map, log, unmatch = fuzzy_match_districts(df, master, source_name)
    
    def apply_map(row):
        key = (row['state_name'], row['district_name'])
        return dist_map.get(key, row['district_name'])
        
    df['district_name'] = df.apply(apply_map, axis=1)
    return df, log, unmatch

def main():
    print("="*60)
    print("  LOADING CLIMATE DATA")
    print("="*60)
    
    master = pd.read_csv(os.path.join(PROC_DIR, 'health_master_v2.csv'))
    
    # ── PART A: Daily Rainfall ──
    csv_path = os.path.join(DATA_DIR, 'Indian Rainfall Dataset District-wise Daily Measurements.csv')
    df_daily = pd.read_csv(csv_path, sep=';', dtype=str)
    
    # Clean string column names
    df_daily.columns = [c.strip('"') for c in df_daily.columns]
    df_daily['state'] = df_daily['state'].str.strip('"')
    df_daily['district'] = df_daily['district'].str.strip('"')
    
    # Extract numerical cols
    day_cols = df_daily.columns[3:]
    for col in day_cols:
        df_daily[col] = pd.to_numeric(df_daily[col].str.strip('"'), errors='coerce').fillna(0)
    
    df_daily['monthly_total'] = df_daily[day_cols].sum(axis=1)
    
    df_daily = df_daily.rename(columns={'state': 'state_name', 'district': 'district_name'})
    agg_csv = df_daily.groupby(['state_name', 'district_name'])['monthly_total'].agg(['sum', 'std']).reset_index()
    agg_csv.rename(columns={'sum': 'csv_annual_rainfall_mm', 'std': 'csv_monthly_rainfall_std'}, inplace=True)
    
    # ── PART B: Timeseries XLS ──
    xls_path = os.path.join(DATA_DIR, 'India_rainfall_District Wise Timeseries_2012_2022.xls')
    warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
    df_xls_raw = pd.read_excel(xls_path, engine='openpyxl', header=None, skiprows=3)
    
    df_xls = df_xls_raw[[0, 1, 2, 3, 4]].copy()
    df_xls.columns = ['state_name', 'district_name', 'xls_actual_mm', 'xls_normal_mm', 'xls_deviation_pct']
    
    # Drop completely empty rows or state total rows (often DISTRICT is NaN or same as State)
    df_xls = df_xls.dropna(subset=['state_name', 'district_name'])
    
    for c in ['xls_actual_mm', 'xls_normal_mm', 'xls_deviation_pct']:
        df_xls[c] = pd.to_numeric(df_xls[c].replace('-', np.nan), errors='coerce')
        
    # ── FUZZY MATCH & JOIN ──
    all_logs = []
    all_unmatched = []
    
    agg_csv, log_c, un_c = clean_dataframe(agg_csv, 'Climate-CSV', master)
    df_xls, log_x, un_x = clean_dataframe(df_xls, 'Climate-XLS', master)
    
    all_logs.extend(log_c)
    all_logs.extend(log_x)
    all_unmatched.extend(un_c)
    all_unmatched.extend(un_x)
    
    # Join CSV
    master = master.merge(agg_csv, on=['state_name', 'district_name'], how='left')
    csv_matched = master['csv_annual_rainfall_mm'].notna().sum()
    
    # Join XLS
    df_xls = df_xls.drop_duplicates(subset=['state_name', 'district_name'])
    master = master.merge(df_xls, on=['state_name', 'district_name'], how='left')
    xls_matched = master['xls_actual_mm'].notna().sum()
    
    # Log unmatched
    unmatched_df = pd.DataFrame(all_unmatched)
    if not unmatched_df.empty:
        unmatched_log_path = os.path.join(PROC_DIR, 'unmatched_climate_log.csv')
        unmatched_df.to_csv(unmatched_log_path, index=False)
    
    # Save Final
    out_path = os.path.join(PROC_DIR, 'climate_master.csv')
    master.to_csv(out_path, index=False)
    
    print("\nFuzzy Matches Made:")
    for log in all_logs[:10]:
         print(f"  [{log['source']}] {log['state']}: {log['source_district']} -> {log['master_district']} ({log['score']:.1f})")
    if len(all_logs) > 10: print(f"  ...and {len(all_logs)-10} more.")
    
    print("\nJoin Results:")
    print(f"  CSV (Daily Rainfall) matched: {csv_matched}/{len(master)} districts")
    print(f"  XLS (Timeseries) matched:     {xls_matched}/{len(master)} districts")
    print(f"\n✅ Saved to {out_path}")
    print(f"Saved unmatched logs to processed_data/unmatched_climate_log.csv")

if __name__ == '__main__':
    main()
