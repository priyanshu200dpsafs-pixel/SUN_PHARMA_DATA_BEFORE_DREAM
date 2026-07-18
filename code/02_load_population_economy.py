"""
02_load_population_economy.py
Loads PCA Census, Economic Census, and VIIRS Nightlights data.
Joins all three onto the geography_master using pc11_state_id + pc11_district_id.
Reports gaps honestly. Does NOT impute or fill anything.
"""

import pandas as pd
import os

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR   = os.path.join(BASE_DIR, 'raw_data', '02_population_economy')
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')
JOIN_KEYS = ['pc11_state_id', 'pc11_district_id']

# ── Helpers ──────────────────────────────────────────────────────────────────
def load_and_audit(path, label, join_keys, dtype_override=None):
    """Load a CSV, print row count + columns, flag duplicate join keys."""
    df = pd.read_csv(path, dtype=str)
    if dtype_override:
        for col, dt in dtype_override.items():
            if col in df.columns:
                df[col] = df[col].astype(dt)

    print(f"\n{'='*60}")
    print(f"  FILE: {label}")
    print(f"{'='*60}")
    print(f"  Rows         : {len(df)}")
    print(f"  Columns ({len(df.columns)}): {list(df.columns)}")

    # Check join-key duplicates
    dups = df.duplicated(subset=join_keys).sum()
    if dups > 0:
        print(f"  ⚠️  WARNING: {dups} duplicate rows on {join_keys}!")
        print(df[df.duplicated(subset=join_keys, keep=False)][join_keys + [df.columns[2]]].head(10).to_string())
    else:
        print(f"  ✅ No duplicate join-key rows.")

    return df


def match_rate(geo_df, src_df, label, join_keys):
    """Report what % of geography_master rows get a match."""
    merged = geo_df.merge(src_df[join_keys].drop_duplicates(),
                          on=join_keys, how='left', indicator=True)
    matched   = (merged['_merge'] == 'both').sum()
    unmatched = (merged['_merge'] == 'left_only').sum()
    total     = len(geo_df)
    print(f"  Match rate vs geography_master — "
          f"{matched}/{total} ({100*matched/total:.1f}%) matched | "
          f"{unmatched} unmatched")


def missing_report(df, label, skip_cols=None):
    """Print % missing per column for newly added columns."""
    skip_cols = skip_cols or []
    new_cols  = [c for c in df.columns if c not in skip_cols]
    miss      = df[new_cols].isnull().mean() * 100
    miss       = miss[miss > 0].sort_values(ascending=False)
    if miss.empty:
        print(f"  ✅ No missing values in {label} columns.")
    else:
        print(f"  Missing % in {label} columns (only columns with gaps shown):")
        for col, pct in miss.items():
            print(f"    {col:<45} {pct:.1f}%")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    # 1. Load geography master (our anchor)
    geo = pd.read_csv(os.path.join(PROC_DIR, 'geography_master.csv'), dtype=str)
    # Drop the dummy 000-state artifact row
    geo = geo[geo['pc11_district_id'] != '000'].copy()
    print(f"\nGeography master loaded: {len(geo)} districts (anchor).")

    # ── A. PCA Population Census ─────────────────────────────────────────────
    pca = load_and_audit(
        os.path.join(RAW_DIR, 'pc11_pca_clean_pc11dist.csv'),
        'PCA Population Census (pc11_pca_clean_pc11dist.csv)',
        JOIN_KEYS
    )
    match_rate(geo, pca, 'PCA', JOIN_KEYS)

    # Keep only the columns most relevant to MAI; flag all are kept
    # (no columns dropped — let later feature-selection script decide)
    master = geo.merge(pca, on=JOIN_KEYS, how='left')

    # ── B. Economic Census 2013 ──────────────────────────────────────────────
    ec13 = load_and_audit(
        os.path.join(RAW_DIR, 'ec13_pc11dist.csv'),
        'Economic Census 2013 (ec13_pc11dist.csv)',
        JOIN_KEYS
    )
    match_rate(geo, ec13, 'EC13', JOIN_KEYS)

    master = master.merge(ec13, on=JOIN_KEYS, how='left')

    # ── C. VIIRS Nightlights ─────────────────────────────────────────────────
    viirs_raw = load_and_audit(
        os.path.join(RAW_DIR, 'viirs_annual_pc11dist.csv'),
        'VIIRS Nightlights (viirs_annual_pc11dist.csv)',
        JOIN_KEYS
    )

    # VIIRS is multi-year / multi-category: filter to year=2020, median-masked
    # 2020 is the latest full year that aligns with NFHS-5 and NCRP data vintage
    VIIRS_YEAR     = '2020'
    VIIRS_CATEGORY = 'median-masked'
    viirs = viirs_raw[
        (viirs_raw['year'] == VIIRS_YEAR) &
        (viirs_raw['category'] == VIIRS_CATEGORY)
    ].copy()

    print(f"\n  ℹ️  VIIRS filtered to year={VIIRS_YEAR}, category='{VIIRS_CATEGORY}'")
    print(f"     Rows after filter: {len(viirs)}")

    # Re-check duplicates after filter
    dups_v = viirs.duplicated(subset=JOIN_KEYS).sum()
    if dups_v > 0:
        print(f"  ⚠️  WARNING: {dups_v} duplicate join-key rows in filtered VIIRS!")
    else:
        print(f"  ✅ No duplicate join-key rows in filtered VIIRS.")

    match_rate(geo, viirs, 'VIIRS', JOIN_KEYS)

    # Drop year + category before merging (they are now constants)
    viirs = viirs.drop(columns=['year', 'category'])
    master = master.merge(viirs, on=JOIN_KEYS, how='left')

    # ── Final Report ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  MERGED TABLE SUMMARY")
    print(f"{'='*60}")
    print(f"  Total rows    : {len(master)}")
    print(f"  Total columns : {len(master.columns)}")

    geo_cols = list(geo.columns)
    print("\n  --- Missing % for PCA columns ---")
    pca_cols = [c for c in pca.columns if c not in JOIN_KEYS]
    missing_report(master, 'PCA', skip_cols=geo_cols + JOIN_KEYS)

    print("\n  --- Missing % for EC13 columns ---")
    ec13_cols = [c for c in ec13.columns if c not in JOIN_KEYS]
    missing_report(master, 'EC13', skip_cols=geo_cols + JOIN_KEYS + pca_cols)

    print("\n  --- Missing % for VIIRS columns ---")
    missing_report(master, 'VIIRS', skip_cols=geo_cols + JOIN_KEYS + pca_cols + ec13_cols)

    # ── Save ─────────────────────────────────────────────────────────────────
    out_path = os.path.join(PROC_DIR, 'population_economy_master.csv')
    master.to_csv(out_path, index=False)
    print(f"\n  ✅ Saved to: {out_path}")
    print(f"\n  SAMPLE ROWS (first 3):")
    print(master[['pc11_state_id', 'pc11_district_id', 'state_name', 'district_name',
                  'pc11_pca_tot_p', 'ec13_emp_all', 'viirs_annual_mean']].head(3).to_string(index=False))


if __name__ == '__main__':
    main()
