"""
03d_manual_alias_fix.py

Applies a manual hardcoded alias table for specific known district name variations
before running the fuzzy matching algorithm.
"""

import pandas as pd
import os
from rapidfuzz import fuzz, process

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')

# Hardcoded alias dictionary (State, Source District) -> Master District
MANUAL_ALIASES = {
    ('KARNATAKA', 'SHIVAMOGGA'): 'SHIMOGA',
    ('MADHYA PRADESH', 'NARSINGHPUR'): 'NARSIMHAPUR',
    ('MAHARASHTRA', 'RAIGAD'): 'RAIGARH',
    ('ODISHA', 'BOUDH'): 'BAUDH',
    ('RAJASTHAN', 'DHOLPUR'): 'DHAULPUR',
    ('WEST BENGAL', 'DARJEELING'): 'DARJILING',
}

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
        
        # Find best match by comparing space-stripped versions
        best_match = None
        best_score = 0
        
        for m_state in unmatched_master:
            m_clean = m_state.replace(' ', '')
            # use fuzz.ratio since we are comparing space-stripped words
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


def apply_manual_aliases(df):
    def mapper(row):
        key = (row['state_name'], row['district_name'])
        return MANUAL_ALIASES.get(key, row['district_name'])
    df['district_name'] = df.apply(mapper, axis=1)
    return df


def main():
    print("="*60)
    print("  APPLYING MANUAL ALIASES & FUZZY MATCHING")
    print("="*60)
    
    master = pd.read_csv(os.path.join(PROC_DIR, 'population_economy_master.csv'), dtype=str)
    
    nfhs6_df = pd.read_csv(os.path.join(PROC_DIR, 'nfhs6_raw.csv'))
    nfhs5_df = pd.read_csv(os.path.join(PROC_DIR, 'nfhs5_raw.csv'))
    rhs_df = pd.read_csv(os.path.join(PROC_DIR, 'rhs_raw.csv'))
    
    all_match_logs = []
    all_unmatched = []
    
    # ── NFHS-6 ──
    nfhs6_df['state_name'] = nfhs6_df['state_name'].str.upper().str.strip()
    nfhs6_map, nfhs6_log, nfhs6_unmatch = fuzzy_match_states(nfhs6_df, master, 'NFHS-6')
    all_match_logs.extend(nfhs6_log)
    all_unmatched.extend(nfhs6_unmatch)
    nfhs6_df['state_name'] = nfhs6_df['state_name'].replace(nfhs6_map)
    
    # ── NFHS-5 ──
    nfhs5_df['district_name'] = nfhs5_df['district_name'].str.upper().str.strip()
    nfhs5_df['state_name'] = nfhs5_df['state_name'].str.upper().str.strip()
    
    nfhs5_state_map, nfhs5_state_log, _ = fuzzy_match_states(nfhs5_df, master, 'NFHS-5 (State)')
    nfhs5_df['state_name'] = nfhs5_df['state_name'].replace(nfhs5_state_map)
    
    nfhs5_df = apply_manual_aliases(nfhs5_df)
    
    nfhs5_map, nfhs5_log, nfhs5_unmatch = fuzzy_match_districts(nfhs5_df, master, 'NFHS-5')
    all_match_logs.extend(nfhs5_log)
    all_unmatched.extend(nfhs5_unmatch)
    
    def apply_nfhs5_map(row):
        key = (row['state_name'], row['district_name'])
        return nfhs5_map.get(key, row['district_name'])
    nfhs5_df['district_name'] = nfhs5_df.apply(apply_nfhs5_map, axis=1)
    
    # ── RHS ──
    rhs_df['rhs_state_name'] = rhs_df['rhs_state_name'].str.upper().str.strip()
    rhs_df['rhs_district_name'] = rhs_df['rhs_district_name'].str.upper().str.strip()
    rhs_df = rhs_df.rename(columns={'rhs_state_name': 'state_name', 'rhs_district_name': 'district_name'})
    
    rhs_state_map, rhs_state_log, _ = fuzzy_match_states(rhs_df, master, 'RHS (State)')
    rhs_df['state_name'] = rhs_df['state_name'].replace(rhs_state_map)
    
    rhs_df = apply_manual_aliases(rhs_df)
    
    rhs_map, rhs_log, rhs_unmatch = fuzzy_match_districts(rhs_df, master, 'RHS')
    all_match_logs.extend(rhs_log)
    all_unmatched.extend(rhs_unmatch)
    
    def apply_rhs_map(row):
        key = (row['state_name'], row['district_name'])
        return rhs_map.get(key, row['district_name'])
    rhs_df['district_name'] = rhs_df.apply(apply_rhs_map, axis=1)
    
    # ── RE-JOIN TO MASTER ──
    master = master.merge(nfhs6_df, on='state_name', how='left')
    nfhs6_cols = [c for c in nfhs6_df.columns if c != 'state_name']
    matched_6 = master[nfhs6_cols[0]].notna().sum() if nfhs6_cols else 0
    print(f"  NFHS-6 join: {matched_6}/{len(master)} districts got state-level data")
    
    nfhs5_cols = [c for c in nfhs5_df.columns if c.startswith('nfhs5_')]
    nfhs5_join = nfhs5_df[['state_name', 'district_name'] + nfhs5_cols].copy()
    nfhs5_join = nfhs5_join.drop_duplicates(subset=['state_name', 'district_name'], keep='first')
    
    master = master.merge(nfhs5_join, on=['state_name', 'district_name'], how='left')
    matched_5 = master[nfhs5_cols[0]].notna().sum() if nfhs5_cols else 0
    print(f"  NFHS-5 join (after aliases & fuzzy): {matched_5}/{len(master)} districts matched")
    
    rhs_cols = [c for c in rhs_df.columns if c.startswith('rhs_') and c not in ('state_name', 'district_name')]
    rhs_join = rhs_df[['state_name', 'district_name'] + rhs_cols].copy()
    rhs_join = rhs_join.drop_duplicates(subset=['state_name', 'district_name'], keep='first')
    
    master = master.merge(rhs_join, on=['state_name', 'district_name'], how='left')
    matched_rhs = master[rhs_cols[0]].notna().sum() if rhs_cols else 0
    print(f"  RHS join (after aliases & fuzzy): {matched_rhs}/{len(master)} districts matched")
    
    out_path = os.path.join(PROC_DIR, 'health_master.csv')
    master.to_csv(out_path, index=False)
    print(f"\n  ✅ Saved improved master to: {out_path}")
    
    unmatched_df = pd.DataFrame(all_unmatched)
    if not unmatched_df.empty:
        unmatched_df.to_csv(os.path.join(PROC_DIR, 'unmatched_districts_log.csv'), index=False)
        print(f"  Saved unmatched log to processed_data/unmatched_districts_log.csv")

if __name__ == '__main__':
    main()
