"""
03c_diagnose_unmatched.py

Diagnoses the unmatched districts from Script 03b and categorizes them.
"""

import pandas as pd
import os
from rapidfuzz import fuzz, process

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')

def main():
    unmatched_path = os.path.join(PROC_DIR, 'unmatched_districts_log.csv')
    if not os.path.exists(unmatched_path):
        print("No unmatched districts log found!")
        return

    unmatched_df = pd.read_csv(unmatched_path)
    master = pd.read_csv(os.path.join(PROC_DIR, 'geography_master.csv'))
    
    master['state_name'] = master['state_name'].str.upper().str.strip()
    master['district_name'] = master['district_name'].str.upper().str.strip()
    
    category_1_2 = []  # Structural mismatch or totally different name (Score < 75)
    category_3 = []    # Near misses (Score 75 - 84)
    state_level_unmatched = []
    
    for _, row in unmatched_df.iterrows():
        source = row['source']
        state = row['state']
        dist = row['district']
        
        if 'STATE LEVEL' in str(dist) or dist == 'N/A (State level)':
            state_level_unmatched.append((source, state, dist))
            continue
            
        master_state = master[master['state_name'] == state]
        if master_state.empty:
            category_1_2.append((source, state, dist, "NO STATE IN MASTER", 0))
            continue
            
        master_dists = master_state['district_name'].tolist()
        
        match = process.extractOne(dist, master_dists, scorer=fuzz.token_sort_ratio)
        if match:
            best_match, score, _ = match
            if 75 <= score < 85:
                category_3.append((source, state, dist, best_match, score))
            else:
                category_1_2.append((source, state, dist, best_match, score))
                
    print("="*60)
    print("  UNMATCHED DISTRICTS DIAGNOSTIC")
    print("="*60)
    print(f"Total Unmatched Entries: {len(unmatched_df)}\n")
    
    print(f"Category 3: Near Misses (Score 75-84) — count: {len(category_3)}")
    print("-" * 60)
    # Sort by state, then score
    category_3.sort(key=lambda x: (x[1], -x[4]))
    for nm in category_3:
        print(f"  [{nm[0]}] {nm[1]}: {nm[2]} -> {nm[3]} (Score: {nm[4]:.1f})")
        
    print(f"\nCategory 1/2: Structural or Totally Different (Score < 75) — count: {len(category_1_2)}")
    print("-" * 60)
    print("  (These are either newly created districts not in the 2011 Census master list,")
    print("   or districts with completely different naming conventions requiring a manual lookup table.)")
    # Print a sample of 15
    for td in category_1_2[:15]:
         print(f"  [{td[0]}] {td[1]}: {td[2]} -> {td[3]} (Score: {td[4]:.1f})")
    if len(category_1_2) > 15:
         print(f"  ... and {len(category_1_2) - 15} more.")

    if state_level_unmatched:
        print(f"\nState-Level Unmatched (NFHS-6) — count: {len(state_level_unmatched)}")
        for su in state_level_unmatched:
            print(f"  [{su[0]}] {su[1]}")

if __name__ == '__main__':
    main()
