"""
05a_extract_pmjay_data.py

Extracts PMBJP (Jan Aushadhi) Kendra counts from state PDFs and joins to master.
"""

import pandas as pd
import os
import pdfplumber
from collections import defaultdict
from rapidfuzz import fuzz, process

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR  = os.path.join(BASE_DIR, 'raw_data', '07_pmbjp')
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


def main():
    print("="*60)
    print("  EXTRACTING PMBJP KENDRA DATA")
    print("="*60)
    
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found in raw_data/07_pmbjp/")
        return
        
    all_data = []
    failed_files = []
    
    for file in pdf_files:
        pdf_path = os.path.join(DATA_DIR, file)
        file_extracted = 0
        state_name = None
        has_error = False
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Some PDFs are completely blank or unparseable
                if len(pdf.pages) == 0:
                    failed_files.append((file, "No pages"))
                    continue
                    
                for page in pdf.pages:
                    table = page.extract_table()
                    if not table:
                        continue
                        
                    # Find column indexes
                    header = table[0]
                    if not header or 'State Name' not in header:
                        # Sometimes header is on the second row
                        if len(table) > 1 and table[1] and 'State Name' in table[1]:
                            header = table[1]
                            table = table[2:]
                        else:
                            # Assume standard structure if "State Name" is missing from header string (sometimes parsed weirdly)
                            # Standard: Sr.No, Kendra Code, Name, State Name, District Name, Pin Code, Address
                            pass 

                    # Safe extraction
                    for row in table:
                        if not row or len(row) < 5:
                            continue
                        
                        # Skip header rows
                        if 'State Name' in str(row[3]) or 'Sr.No' in str(row[0]):
                            continue
                            
                        state_val = str(row[3]).strip().replace('\n', ' ')
                        dist_val = str(row[4]).strip().replace('\n', ' ')
                        
                        if state_val and dist_val and state_val.lower() != 'none':
                            all_data.append({
                                'state_name': state_val,
                                'district_name': dist_val
                            })
                            file_extracted += 1
                            if not state_name:
                                state_name = state_val
                                
        except Exception as e:
            failed_files.append((file, str(e)))
            has_error = True
            
        if not has_error and file_extracted == 0:
            failed_files.append((file, "No data extracted"))
            
        status = "❌ FAILED" if has_error or file_extracted == 0 else f"✅ {file_extracted} Kendras extracted"
        state_label = f"({state_name})" if state_name else ""
        print(f"  {file} {state_label}: {status}")
        
    print(f"\nProcessing Complete. {len(failed_files)} / {len(pdf_files)} failed.")
    
    if len(failed_files) / len(pdf_files) > 0.2:
        print("CRITICAL: More than 20% of state PDFs failed to parse!")
        print("Failed files:")
        for f, err in failed_files:
            print(f"  - {f}: {err}")
        return
        
    if not all_data:
        print("No data extracted at all.")
        return
        
    # Aggregate into district counts
    df_raw = pd.DataFrame(all_data)
    df = df_raw.groupby(['state_name', 'district_name']).size().reset_index(name='pmbjp_kendra_count')
    
    print(f"\nTotal districts with Kendra data: {len(df)}")
    
    # ── STANDARDIZE & JOIN ──
    df['state_name'] = df['state_name'].str.upper()
    df['district_name'] = df['district_name'].str.upper()
    
    master_path = os.path.join(PROC_DIR, 'health_master_v2.csv')
    master = pd.read_csv(master_path)
    
    # Fuzzy match state
    state_map, state_log, _ = fuzzy_match_states(df, master, 'PMBJP (State)')
    df['state_name'] = df['state_name'].replace(state_map)
    for log in state_log:
        print(f"  State Match: {log['state']} -> {log['master_district']} ({log['score']})")
        
    # Apply manual aliases if any needed for PMBJP
    MANUAL_ALIASES = {
        ('KARNATAKA', 'SHIVAMOGGA'): 'SHIMOGA',
        ('MADHYA PRADESH', 'NARSINGHPUR'): 'NARSIMHAPUR',
        ('MAHARASHTRA', 'RAIGAD'): 'RAIGARH',
        ('ODISHA', 'BOUDH'): 'BAUDH',
        ('RAJASTHAN', 'DHOLPUR'): 'DHAULPUR',
        ('WEST BENGAL', 'DARJEELING'): 'DARJILING',
        ('ANDAMAN & NICOBAR ISLANDS', 'SOUTH ANDAMANS'): 'SOUTH ANDAMAN',
        ('ANDAMAN & NICOBAR ISLANDS', 'NORTH AND MIDDLE ANDAMAN'): 'NORTH & MIDDLE ANDAMAN',
    }
    def alias_mapper(row):
        key = (row['state_name'], row['district_name'])
        return MANUAL_ALIASES.get(key, row['district_name'])
    df['district_name'] = df.apply(alias_mapper, axis=1)
    
    # Fuzzy match districts
    dist_map, dist_log, dist_unmatch = fuzzy_match_districts(df, master, 'PMBJP')
    def apply_dist_map(row):
        key = (row['state_name'], row['district_name'])
        return dist_map.get(key, row['district_name'])
    df['district_name'] = df.apply(apply_dist_map, axis=1)
    
    for log in dist_log[:10]:
        print(f"  Fuzzy Match: {log['state']}: {log['source_district']} -> {log['master_district']} ({log['score']:.1f})")
    if len(dist_log) > 10: print(f"  ...and {len(dist_log)-10} more.")
    
    # Join
    master = master.merge(df, on=['state_name', 'district_name'], how='left')
    matched = master['pmbjp_kendra_count'].notna().sum()
    
    print(f"\nFinal Match Rate: {matched} / {len(master)} districts matched exact or via fuzzy logic.")
    
    out_path = os.path.join(PROC_DIR, 'pmbjp_master.csv')
    master.to_csv(out_path, index=False)
    print(f"✅ Saved to {out_path}")
    
    unmatched_df = pd.DataFrame(dist_unmatch)
    if not unmatched_df.empty:
        unmatched_log_path = os.path.join(PROC_DIR, 'unmatched_pmbjp_log.csv')
        unmatched_df.to_csv(unmatched_log_path, index=False)

if __name__ == '__main__':
    main()
