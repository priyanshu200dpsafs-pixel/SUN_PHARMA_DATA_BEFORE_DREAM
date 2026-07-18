"""
03_extract_health_data.py  (v2 — fixed parsing)

Extracts health data from three PDF sources:
  PART A: NFHS-6 (India-wide PDF) — STATE-level fact sheets
  PART B: NFHS-5 (36 state PDFs) — DISTRICT-level fact sheets
  PART C: RHS 2021-22 — DISTRICT-level health infrastructure (Table 6)

Joins onto processed_data/population_economy_master.csv.
Saves to processed_data/health_master.csv.
"""

import pandas as pd
import pdfplumber
import re
import os
import sys

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR   = os.path.join(BASE_DIR, 'raw_data')
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')


# ══════════════════════════════════════════════════════════════════════════════
# PART A: NFHS-6 — State-level extraction
# ══════════════════════════════════════════════════════════════════════════════

# Target indicators and which value position to grab
# Format: indicator_number -> (column_name, value_position)
# value_position: for state sheets with Urban/Rural/Total/NFHS5, "Total" is index 2
NFHS6_TARGETS = {
    '38': 'nfhs6_institutional_births',
    '76': 'nfhs6_overweight_women',
    '77': 'nfhs6_overweight_men',
    '80': 'nfhs6_diabetes_women',
    '83': 'nfhs6_diabetes_men',
    '86': 'nfhs6_hypertension_women',
    '89': 'nfhs6_hypertension_men',
}


def extract_nfhs6_state_data(pdf_path):
    """Extract state-level indicators from NFHS-6 India PDF."""
    print("\n" + "="*60)
    print("  PART A: NFHS-6 (State-level)")
    print("="*60)
    
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"  Total pages: {total_pages}")
        
        current_state = None
        state_data = {}
        
        for page_idx in range(total_pages):
            text = pdf.pages[page_idx].extract_text() or ''
            lines = text.split('\n')
            
            # Detect state from header
            first_line = lines[0].strip() if lines else ''
            header_match = re.match(r'^(.+?)\s*[-–—]\s*Key Indicators', first_line)
            if header_match:
                state_name = header_match.group(1).strip().upper()
                if state_name == 'INDIA':
                    current_state = 'INDIA'  # still parse it
                elif ',' in state_name:
                    continue  # skip district-level pages if any
                else:
                    if current_state and current_state != state_name and state_data:
                        # Save previous state
                        if len(state_data) > 1:
                            results.append(state_data.copy())
                    current_state = state_name
                    state_data = {'state_name': current_state}
            
            if not current_state:
                continue
            
            # Parse indicators — handle multi-line indicators
            for i, line in enumerate(lines):
                line_s = line.strip()
                for ind_num, col_name in NFHS6_TARGETS.items():
                    if not re.match(rf'^{ind_num}\.\s', line_s):
                        continue
                    
                    # Helper to check if string is a number format used in factsheets
                    def is_num(s):
                        return re.match(r'^(\d+\.\d+|\*|na)$', s)
                    
                    # Try to extract contiguous numbers from end of current line
                    parts = line_s.split()
                    nums = []
                    for part in reversed(parts):
                        if is_num(part):
                            nums.insert(0, part)
                        else:
                            break
                    
                    if len(nums) < 3 and i + 1 < len(lines):
                        # Try next line
                        next_line = lines[i+1].strip()
                        next_parts = next_line.split()
                        next_nums = [p for p in next_parts if is_num(p)]
                        if len(next_nums) >= 3:
                            nums = next_nums
                    
                    if len(nums) >= 3:
                        # For state sheets, numbers are Urban, Rural, Total, [NFHS-5]
                        total_val = nums[-2] if len(nums) >= 4 else nums[-1]
                        if total_val not in ('*', 'na'):
                            try:
                                state_data[col_name] = float(total_val)
                            except ValueError:
                                pass
        
        # Save last state
        if state_data and len(state_data) > 1:
            results.append(state_data.copy())
    
    # Remove "INDIA" row — we only want states
    df = pd.DataFrame(results)
    df = df[df['state_name'] != 'INDIA'].copy()
    
    print(f"  States extracted: {len(df)}")
    if not df.empty:
        for col in [c for c in df.columns if c != 'state_name']:
            non_null = df[col].notna().sum()
            print(f"    {col}: {non_null}/{len(df)} states")
        print(f"\n  Sample (first 5):")
        print(df.head(5).to_string(index=False))
    
    return df


# ══════════════════════════════════════════════════════════════════════════════
# PART B: NFHS-5 — District-level extraction
# ══════════════════════════════════════════════════════════════════════════════

NFHS5_TARGETS = {
    '37': 'nfhs5_institutional_births',
    '79': 'nfhs5_overweight_women',
    '88': 'nfhs5_diabetes_women',
    '91': 'nfhs5_diabetes_men',
    '94': 'nfhs5_hypertension_women',
    '97': 'nfhs5_hypertension_men',
    '98': 'nfhs5_cancer_screening_cervical',
    '99': 'nfhs5_cancer_screening_breast',
}


def extract_nfhs5_district_data(pdf_dir):
    """Extract district-level indicators from NFHS-5 state PDFs."""
    print("\n" + "="*60)
    print("  PART B: NFHS-5 (District-level)")
    print("="*60)
    
    pdf_files = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    print(f"  Found {len(pdf_files)} PDF files")
    
    all_districts = []
    failed_files = []
    skipped_duplicates = []
    seen_states = set()
    
    for pdf_file in pdf_files:
        if '(1)' in pdf_file:
            skipped_duplicates.append(pdf_file)
            continue
        
        state_name = _guess_state_from_filename(pdf_file)
        if state_name in seen_states:
            skipped_duplicates.append(pdf_file)
            continue
        seen_states.add(state_name)
        
        pdf_path = os.path.join(pdf_dir, pdf_file)
        try:
            districts = _parse_nfhs5_pdf(pdf_path)
            all_districts.extend(districts)
            n = len(districts)
            status = "✅" if n > 0 else "⚠️  0 districts"
            print(f"    {status}  {pdf_file[:55]:<55} → {n} districts")
        except Exception as e:
            failed_files.append((pdf_file, str(e)))
            print(f"    ❌  {pdf_file[:55]:<55} → FAILED: {e}")
    
    print(f"\n  Total districts extracted: {len(all_districts)}")
    if skipped_duplicates:
        print(f"  Skipped duplicates: {skipped_duplicates}")
    
    if failed_files:
        print(f"\n  ⚠️  FAILED FILES ({len(failed_files)}):")
        for f, err in failed_files:
            print(f"    - {f}: {err}")
    
    # 20% failure check
    total_attempted = len(pdf_files) - len(skipped_duplicates)
    if failed_files and len(failed_files) / total_attempted > 0.20:
        print(f"\n  🛑 CRITICAL: {len(failed_files)}/{total_attempted} failed (>20%). STOPPING.")
        sys.exit(1)
    
    df = pd.DataFrame(all_districts)
    if not df.empty:
        indicator_cols = [c for c in df.columns if c.startswith('nfhs5_')]
        print(f"\n  Indicator coverage:")
        for col in indicator_cols:
            non_null = df[col].notna().sum()
            print(f"    {col}: {non_null}/{len(df)} ({100*non_null/len(df):.1f}%)")
        print(f"\n  Sample (first 5):")
        sample_cols = ['state_name', 'district_name'] + indicator_cols[:4]
        print(df[sample_cols].head(5).to_string(index=False))
    
    return df


def _guess_state_from_filename(filename):
    match = re.search(r'NFHS-5_StateFact_(.+?)__', filename)
    if match:
        return match.group(1).strip().upper()
    return filename.upper()


def _parse_nfhs5_pdf(pdf_path):
    """Parse a single NFHS-5 state PDF for district-level indicators."""
    districts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        current_district = None
        current_state = None
        district_data = {}
        
        for page_idx in range(len(pdf.pages)):
            text = pdf.pages[page_idx].extract_text() or ''
            lines = text.split('\n')
            
            if not lines:
                continue
            
            first_line = lines[0].strip()
            
            # Detect district header: "DistrictName, StateName - Key Indicators"
            dist_match = re.match(r'^(.+?),\s*(.+?)\s*[-–—]\s*Key Indicators', first_line)
            # Detect state header: "StateName - Key Indicators" (no comma)
            state_match = re.match(r'^(.+?)\s*[-–—]\s*Key Indicators', first_line)
            
            if dist_match:
                new_district = dist_match.group(1).strip().upper()
                new_state = dist_match.group(2).strip().upper()
                
                # If this is a NEW district (different from current), save the old one
                if current_district and new_district != current_district:
                    if len(district_data) > 2:
                        districts.append(district_data.copy())
                    district_data = {}
                
                current_district = new_district
                current_state = new_state
                if 'district_name' not in district_data:
                    district_data = {
                        'district_name': current_district,
                        'state_name': current_state,
                    }
                # DO NOT continue — parse indicators on this same page
                
            elif state_match and ',' not in state_match.group(1):
                # State-level page — save any pending district and reset
                if current_district and len(district_data) > 2:
                    districts.append(district_data.copy())
                current_district = None
                district_data = {}
                continue
            
            if not current_district:
                continue
            
            # Parse indicators on this page
            # District sheets have only Total and NFHS-4 columns (2 value columns)
            for i, line in enumerate(lines):
                line_s = line.strip()
                for ind_num, col_name in NFHS5_TARGETS.items():
                    if not re.match(rf'^{ind_num}\.\s', line_s):
                        continue
                    
                    # Combine with next line for multi-line indicators
                    combined = line_s
                    if i + 1 < len(lines):
                        combined = combined + ' ' + lines[i + 1].strip()
                    
                    # Split at (%) to get value portion
                    parts = combined.split('(%)')
                    if len(parts) >= 2:
                        value_text = parts[-1].strip()
                    else:
                        value_text = combined
                    
                    vals = re.findall(r'(\d+\.?\d*)', value_text)
                    
                    # For district sheets: Total is the FIRST number after (%)
                    if vals:
                        raw = vals[0]
                        try:
                            val = float(raw)
                            # Sanity check: percentages should be 0-100
                            if 0 <= val <= 100:
                                district_data[col_name] = val
                        except ValueError:
                            pass
        
        # Save last district
        if current_district and len(district_data) > 2:
            districts.append(district_data.copy())
    
    return districts


# ══════════════════════════════════════════════════════════════════════════════
# PART C: RHS — District-level health infrastructure
# ══════════════════════════════════════════════════════════════════════════════

# Known state serial number mapping for RHS Table 6
RHS_STATE_MAP = {
    1: 'ANDHRA PRADESH', 2: 'ARUNACHAL PRADESH', 3: 'ASSAM', 4: 'BIHAR',
    5: 'CHHATTISGARH', 6: 'GOA', 7: 'GUJARAT', 8: 'HARYANA',
    9: 'HIMACHAL PRADESH', 10: 'JHARKHAND', 11: 'KARNATAKA', 12: 'KERALA',
    13: 'MADHYA PRADESH', 14: 'MAHARASHTRA', 15: 'MANIPUR', 16: 'MEGHALAYA',
    17: 'MIZORAM', 18: 'NAGALAND', 19: 'ODISHA', 20: 'PUNJAB',
    21: 'RAJASTHAN', 22: 'SIKKIM', 23: 'TAMIL NADU', 24: 'TELANGANA',
    25: 'TRIPURA', 26: 'UTTARAKHAND', 27: 'UTTAR PRADESH', 28: 'WEST BENGAL',
    29: 'ANDAMAN AND NICOBAR', 30: 'CHANDIGARH', 31: 'DADRA AND NAGAR HAVELI',
    32: 'DELHI', 33: 'JAMMU AND KASHMIR', 34: 'LADAKH', 35: 'LAKSHADWEEP',
    36: 'PUDUCHERRY',
}

# State name patterns for detection in text lines
STATE_PATTERNS = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya',
    'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim',
    'Tamil Nadu', 'Telangana', 'Tripura', 'Uttarakhand', 'Uttar Pradesh',
    'West Bengal', 'Andaman', 'Chandigarh', 'Dadra', 'Delhi',
    'Jammu', 'Ladakh', 'Lakshadweep', 'Puducherry',
]


def extract_rhs_district_data(pdf_path):
    """Extract district-level SC/PHC/CHC/SDH/DH counts from RHS Table 6."""
    print("\n" + "="*60)
    print("  PART C: RHS 2021-22 (District-level infrastructure)")
    print("="*60)
    print("  Data level: DISTRICT")
    print("  Source: Table 6 — SC, PHC, CHC, SDH, DH counts")
    
    districts = []
    current_state = None
    
    # Skip keywords that appear in header lines
    SKIP_KEYWORDS = ['Number of functional', 'Sub Centres', 'States/Union',
                     'Name of the District', 'Sub Divisional', 'Hospital Hospital',
                     'As on 31st', 'Table 6']
    
    with pdfplumber.open(pdf_path) as pdf:
        # Table 6 spans roughly pages 117-128 (0-indexed: 116-127)
        for page_idx in range(115, min(135, len(pdf.pages))):
            text = pdf.pages[page_idx].extract_text() or ''
            
            # Quick check: is this a Table 6 page?
            if page_idx == 115:
                # First page — check it has the right content
                if 'Sub Centres' not in text and 'PHCs' not in text:
                    continue
            
            lines = text.split('\n')
            
            for line in lines:
                line_s = line.strip()
                
                # Skip empty lines and pure numbers (page numbers)
                if not line_s or re.match(r'^\d{1,3}$', line_s):
                    continue
                
                # Skip header lines
                if any(kw in line_s for kw in SKIP_KEYWORDS):
                    continue
                
                # Skip "Total Districts = N" summary lines
                if 'Total Districts' in line_s or 'Total District' in line_s:
                    continue
                
                # Skip "S No." header fragments
                if re.match(r'^S\s', line_s) or re.match(r'^No\.\s', line_s):
                    continue
                
                # Detect state changes
                # Pattern: "SerialNo StateName DistrictName nums..." 
                # e.g., "8 Haryana Ambala 106 22 5 2 1"
                state_line_match = re.match(r'^(\d{1,2})\s+(.+)', line_s)
                if state_line_match:
                    serial = int(state_line_match.group(1))
                    rest = state_line_match.group(2)
                    
                    # Check if a known state name starts this remainder
                    for sp in STATE_PATTERNS:
                        if rest.startswith(sp):
                            current_state = sp.upper()
                            # After state name, the rest is district + numbers
                            after_state = rest[len(sp):].strip()
                            
                            if after_state:
                                # Parse district data from remainder
                                d = _parse_rhs_district_line(after_state, current_state)
                                if d:
                                    districts.append(d)
                            break
                    else:
                        # Serial number but not a state — could be a page number
                        # Or a line like "Pradesh Anantapur 1311..."
                        # Check if it looks like a continuation
                        if serial > 36:
                            # Too high for state serial — might be data
                            pass
                    continue
                
                # Check for continuation state names (multi-word states split across lines)
                # e.g., "Pradesh" alone on a line after "Himachal"
                if line_s in ('Pradesh', 'Bengal', 'Nadu'):
                    continue
                
                # Regular district data line: "DistrictName num num num num num"
                d = _parse_rhs_district_line(line_s, current_state)
                if d:
                    districts.append(d)
    
    df = pd.DataFrame(districts)
    print(f"\n  Districts extracted: {len(df)}")
    if not df.empty:
        for col in ['rhs_sub_centres', 'rhs_phcs', 'rhs_chcs', 'rhs_sdh', 'rhs_dh']:
            if col in df.columns:
                non_null = df[col].notna().sum()
                print(f"    {col}: {non_null}/{len(df)} ({100*non_null/len(df):.1f}%)")
        
        # Show states found
        states_found = df['rhs_state_name'].nunique()
        print(f"\n  States/UTs covered: {states_found}")
        print(f"\n  Sample (first 5):")
        print(df.head(5).to_string(index=False))
    
    return df


def _parse_rhs_district_line(line, current_state):
    """Parse a single line of RHS data: 'DistrictName num num num num num'."""
    # Must start with a letter
    if not line or not line[0].isalpha():
        return None
    
    # Extract the text portion (district name) and numeric portion
    # Match: one or more words followed by numbers
    match = re.match(r'^([A-Za-z][\w\s().&\'\-]+?)\s+(\d[\d\s]+)$', line)
    if not match:
        return None
    
    dist_name = match.group(1).strip()
    num_str = match.group(2).strip()
    nums = [int(x) for x in num_str.split()]
    
    if len(nums) < 5:
        return None
    
    # Sanity: district names shouldn't be too short or numeric-looking
    if len(dist_name) < 2:
        return None
    
    return {
        'rhs_state_name': current_state,
        'rhs_district_name': dist_name.upper(),
        'rhs_sub_centres': nums[-5],
        'rhs_phcs': nums[-4],
        'rhs_chcs': nums[-3],
        'rhs_sdh': nums[-2],
        'rhs_dh': nums[-1],
    }


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Join everything
# ══════════════════════════════════════════════════════════════════════════════

def main():
    master = pd.read_csv(os.path.join(PROC_DIR, 'population_economy_master.csv'), dtype=str)
    print(f"Loaded population_economy_master: {len(master)} rows, {len(master.columns)} cols")
    
    # ── PART A: NFHS-6 (state-level) ──
    nfhs6_df = extract_nfhs6_state_data(
        os.path.join(RAW_DIR, '03_health_nfhs', 'nfhs6_india.pdf')
    )
    
    if not nfhs6_df.empty:
        nfhs6_df.to_csv(os.path.join(PROC_DIR, 'nfhs6_raw.csv'), index=False)
        master = master.merge(nfhs6_df, on='state_name', how='left')
        nfhs6_cols = [c for c in nfhs6_df.columns if c != 'state_name']
        matched = master[nfhs6_cols[0]].notna().sum() if nfhs6_cols else 0
        print(f"\n  NFHS-6 join: {matched}/{len(master)} districts got state-level data")
    
    # ── PART B: NFHS-5 (district-level) ──
    nfhs5_df = extract_nfhs5_district_data(
        os.path.join(RAW_DIR, '03_health_nfhs', 'nfhs5_state_pdfs')
    )
    
    if not nfhs5_df.empty:
        nfhs5_df.to_csv(os.path.join(PROC_DIR, 'nfhs5_raw.csv'), index=False)
        nfhs5_df['district_name'] = nfhs5_df['district_name'].str.upper().str.strip()
        nfhs5_df['state_name'] = nfhs5_df['state_name'].str.upper().str.strip()
        
        nfhs5_cols = [c for c in nfhs5_df.columns if c.startswith('nfhs5_')]
        nfhs5_join = nfhs5_df[['state_name', 'district_name'] + nfhs5_cols].copy()
        nfhs5_join = nfhs5_join.drop_duplicates(subset=['state_name', 'district_name'], keep='first')
        
        master = master.merge(nfhs5_join, on=['state_name', 'district_name'], how='left')
        matched = master[nfhs5_cols[0]].notna().sum() if nfhs5_cols else 0
        print(f"\n  NFHS-5 join (exact match): {matched}/{len(master)} districts matched")
        print(f"  Unmatched: {len(master) - matched} (may need fuzzy matching later)")
    
    # ── PART C: RHS (district-level) ──
    rhs_df = extract_rhs_district_data(
        os.path.join(RAW_DIR, '04_health_infrastructure', 'RHS.pdf')
    )
    
    if not rhs_df.empty:
        rhs_df.to_csv(os.path.join(PROC_DIR, 'rhs_raw.csv'), index=False)
        rhs_cols = [c for c in rhs_df.columns if c.startswith('rhs_') and c not in ('rhs_state_name', 'rhs_district_name')]
        rhs_join = rhs_df[['rhs_state_name', 'rhs_district_name'] + rhs_cols].copy()
        rhs_join = rhs_join.drop_duplicates(subset=['rhs_state_name', 'rhs_district_name'], keep='first')
        rhs_join = rhs_join.rename(columns={'rhs_state_name': 'state_name', 'rhs_district_name': 'district_name'})
        
        master = master.merge(rhs_join, on=['state_name', 'district_name'], how='left')
        matched = master[rhs_cols[0]].notna().sum() if rhs_cols else 0
        print(f"\n  RHS join (exact match): {matched}/{len(master)} districts matched")
    
    # ── Final Report ──
    print("\n" + "="*60)
    print("  FINAL HEALTH MASTER SUMMARY")
    print("="*60)
    print(f"  Total rows: {len(master)}")
    print(f"  Total columns: {len(master.columns)}")
    
    health_cols = [c for c in master.columns if any(c.startswith(p) for p in ('nfhs5_', 'nfhs6_', 'rhs_'))]
    print(f"\n  Health columns added: {len(health_cols)}")
    print(f"  Missing % per health column:")
    for col in health_cols:
        miss = master[col].isna().sum()
        pct = 100 * miss / len(master)
        print(f"    {col:<45} {pct:.1f}% missing")
    
    out_path = os.path.join(PROC_DIR, 'health_master.csv')
    master.to_csv(out_path, index=False)
    print(f"\n  ✅ Saved to: {out_path}")


if __name__ == '__main__':
    main()
