"""
04_extract_ncrp_data.py

Extracts cancer incidence data from NCRP 2020 PDF and joins to health_master.
Does not impute missing values for non-registry districts.
"""

import pandas as pd
import os
import re
import pdfplumber

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR  = os.path.join(BASE_DIR, 'raw_data', '05_disease_registry')
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')

NCRP_MAP = {
    'Delhi': [('DELHI', d) for d in ['NORTH WEST', 'NORTH', 'NORTH EAST', 'EAST', 'NEW DELHI', 'CENTRAL', 'WEST', 'SOUTH WEST', 'SOUTH']],
    'Patiala district': [('PUNJAB', 'PATIALA')],
    'Hyderabad district': [('ANDHRA PRADESH', 'HYDERABAD')],
    'Kollam district': [('KERALA', 'KOLLAM')],
    'Thi\'puram district': [('KERALA', 'THIRUVANANTHAPURAM')],
    'Bangalore': [('KARNATAKA', 'BANGALORE')],
    'Chennai': [('TAMIL NADU', 'CHENNAI')],
    'Kolkata': [('WEST BENGAL', 'KOLKATA')],
    'Ahmedabad urban': [('GUJARAT', 'AHMADABAD')],
    'Aurangabad': [('MAHARASHTRA', 'AURANGABAD')],
    'Osmanabad & Beed': [('MAHARASHTRA', 'OSMANABAD'), ('MAHARASHTRA', 'BID')],
    'Barshi rural': [('MAHARASHTRA', 'SOLAPUR')],
    'Mumbai': [('MAHARASHTRA', 'MUMBAI')],
    'Pune': [('MAHARASHTRA', 'PUNE')],
    'Wardha district': [('MAHARASHTRA', 'WARDHA')],
    'Bhopal': [('MADHYA PRADESH', 'BHOPAL')],
    'Nagpur': [('MAHARASHTRA', 'NAGPUR')],
    'Manipur state': [('MANIPUR', 'ALL')],
    'Imphal West district': [('MANIPUR', 'IMPHAL WEST')],
    'Mizoram state': [('MIZORAM', 'ALL')],
    'Aizawl district': [('MIZORAM', 'AIZAWL')],
    'Sikkim state': [('SIKKIM', 'ALL')],
    'Tripura state': [('TRIPURA', 'ALL')],
    'West Arunachal': [], # Skipping vague sub-state region
    'Papumpare district': [('ARUNACHAL PRADESH', 'PAPUM PARE')],
    'Meghalaya': [('MEGHALAYA', 'ALL')],
    'East Khasi Hills district': [('MEGHALAYA', 'EAST KHASI HILLS')],
    'Nagaland': [('NAGALAND', 'ALL')],
    'Pasighat': [('ARUNACHAL PRADESH', 'EAST SIANG')],
    'Cachar district': [('ASSAM', 'CACHAR')],
    'Dibrugarh district': [('ASSAM', 'DIBRUGARH')],
    'Kamrup urban': [('ASSAM', 'KAMRUP METROPOLITAN')]
}

def main():
    print("="*60)
    print("  EXTRACTING NCRP 2020 DATA")
    print("="*60)
    
    pdf_path = os.path.join(DATA_DIR, 'NCRP_2020_2012_16.pdf')
    
    # 1. Extract raw data from PDF
    extracted = []
    
    # Pattern to match table rows on Page 32 (index 31)
    # E.g. "1 Delhi (2012-2014) 112.3 147.0 232.2 119.6 141.0 279.0"
    pattern = r'^(?:\d+\s+)?([A-Za-z\s\'\&’]+)\s+\(\d{4}-\d{4}\)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)$'
    
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[32].extract_text()
        if text:
            for line in text.split('\n'):
                match = re.match(pattern, line.strip())
                if match:
                    reg_name = match.group(1).strip()
                    vals = match.groups()[1:]
                    extracted.append({
                        'registry': reg_name,
                        'ncrp_male_cr': float(vals[0]),
                        'ncrp_male_aar': float(vals[1]),
                        'ncrp_male_tr': float(vals[2]),
                        'ncrp_female_cr': float(vals[3]),
                        'ncrp_female_aar': float(vals[4]),
                        'ncrp_female_tr': float(vals[5])
                    })
                    
    print(f"Parsed {len(extracted)} registries from PDF.")
    
    # 2. Join to Master
    master_path = os.path.join(PROC_DIR, 'health_master.csv')
    master = pd.read_csv(master_path)
    
    # Initialize NCRP columns
    cols = ['ncrp_male_cr', 'ncrp_male_aar', 'ncrp_male_tr', 'ncrp_female_cr', 'ncrp_female_aar', 'ncrp_female_tr']
    for c in cols:
        master[c] = None
        
    mapped_count = 0
    mapped_districts = set()
    
    # Apply in order so specific districts overwrite 'ALL' state-level entries
    for row in extracted:
        reg = row['registry']
        # Normalize the curved apostrophe to normal
        reg = reg.replace('’', "'")
        
        if reg not in NCRP_MAP:
            print(f"Warning: Extracted registry '{reg}' not in hardcoded map!")
            continue
            
        targets = NCRP_MAP[reg]
        for st, dist in targets:
            if dist == 'ALL':
                # Apply to all districts in this state
                mask = (master['state_name'] == st)
            else:
                # Apply to specific district
                mask = (master['state_name'] == st) & (master['district_name'] == dist)
                
            affected = master.index[mask].tolist()
            if not affected:
                print(f"  Warning: Target {st} | {dist} not found in master list.")
            
            for idx in affected:
                for c in cols:
                    master.at[idx, c] = row[c]
                mapped_districts.add((master.at[idx, 'state_name'], master.at[idx, 'district_name']))
    
    # Flag column
    master['has_ncrp_data'] = master[cols[0]].notna()
    
    out_path = os.path.join(PROC_DIR, 'health_master_v2.csv')
    master.to_csv(out_path, index=False)
    
    print("\nExtraction Summary:")
    print(f"Total districts with NCRP data mapped: {len(mapped_districts)}")
    print(f"Total districts left NULL (no registry): {len(master) - len(mapped_districts)}")
    print(f"\n✅ Saved to {out_path}")
    print("\nSample mapped districts:")
    print(sorted(list(mapped_districts))[:10])

if __name__ == '__main__':
    main()
