"""
07_variable_selection.py

Selects and curates a final slim table of specific variables, blending
data from NFHS-5 and NFHS-6 where necessary.
"""

import pandas as pd
import os

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROC_DIR  = os.path.join(BASE_DIR, 'processed_data')

def main():
    print("="*60)
    print("  SELECTING FINAL VARIABLES")
    print("="*60)
    
    master_path = os.path.join(PROC_DIR, 'master_table_v1.csv')
    df = pd.read_csv(master_path)
    
    # We will build a new dataframe column by column
    final_df = pd.DataFrame()
    final_df['state_name'] = df['state_name']
    final_df['district_name'] = df['district_name']
    
    justifications = []
    def add_var(col_name, series, reason):
        final_df[col_name] = series
        justifications.append(f"- {col_name}: {reason}")
    
    # ── MACRO/DEMOGRAPHIC ──
    add_var('macro_population', df['pc11_pca_tot_p'], "Total district population (PCA 2011) to normalize absolute counts.")
    
    # Literacy Rate
    if 'pc11_pca_p_lit' in df.columns:
        lit_rate = (df['pc11_pca_p_lit'] / df['pc11_pca_tot_p']) * 100
        add_var('macro_literacy_rate', lit_rate, "Percentage of literate population, proxy for education and health awareness.")
        
    add_var('macro_economic_establishments', df['ec13_count_all'], "Total economic establishments (EC13), proxy for urbanization/development.")
    add_var('macro_economic_employees', df['ec13_emp_all'], "Total formal/informal employees (EC13), proxy for economic activity.")
    add_var('macro_nightlights_mean', df['viirs_annual_mean'], "Annual mean nightlights intensity (VIIRS), modern proxy for wealth and infrastructure.")
    
    # ── DISEASE BURDEN / CHRONIC ──
    # Blend NFHS-5 and NFHS-6
    # Diabetes
    nfhs5_diab = df[['nfhs5_diabetes_women', 'nfhs5_diabetes_men']].mean(axis=1)
    nfhs6_diab = df[['nfhs6_diabetes_women', 'nfhs6_diabetes_men']].mean(axis=1)
    diab_blend = nfhs5_diab.fillna(nfhs6_diab)
    diab_source = ['NFHS-5 (District)' if pd.notna(x) else 'NFHS-6 (State)' if pd.notna(y) else None 
                   for x, y in zip(nfhs5_diab, nfhs6_diab)]
    add_var('chronic_diabetes_prevalence', diab_blend, "Blended diabetes prevalence (Avg of men/women), prioritizing NFHS-5 district data with NFHS-6 state fallback.")
    add_var('chronic_diabetes_source', pd.Series(diab_source), "Data source flag for diabetes prevalence.")
    
    # Hypertension
    nfhs5_hyp = df[['nfhs5_hypertension_women', 'nfhs5_hypertension_men']].mean(axis=1)
    nfhs6_hyp = df[['nfhs6_hypertension_women', 'nfhs6_hypertension_men']].mean(axis=1)
    hyp_blend = nfhs5_hyp.fillna(nfhs6_hyp)
    hyp_source = ['NFHS-5 (District)' if pd.notna(x) else 'NFHS-6 (State)' if pd.notna(y) else None 
                  for x, y in zip(nfhs5_hyp, nfhs6_hyp)]
    add_var('chronic_hypertension_prevalence', hyp_blend, "Blended hypertension prevalence, prioritizing NFHS-5 district data with NFHS-6 state fallback.")
    add_var('chronic_hypertension_source', pd.Series(hyp_source), "Data source flag for hypertension prevalence.")
    
    # Cancer Incidence (NCRP)
    if 'ncrp_male_aar' in df.columns and 'ncrp_female_aar' in df.columns:
        ncrp_avg = df[['ncrp_male_aar', 'ncrp_female_aar']].mean(axis=1)
        add_var('chronic_cancer_incidence_aar', ncrp_avg, "Average Age-Adjusted Rate (AAR) for cancer incidence from NCRP (only available for ~74 districts).")
        
    # ── ACUTE / INFRASTRUCTURE ──
    hosp = df['rhs_sdh'].fillna(0) + df['rhs_dh'].fillna(0)
    # Restore NaN if both were NaN originally
    hosp = hosp.where(df['rhs_sdh'].notna() | df['rhs_dh'].notna(), pd.NA)
    add_var('infra_hospitals_count', hosp, "Combined count of Sub-Divisional and District Hospitals (RHS), indicating advanced healthcare capacity.")
    
    phc_chc = df['rhs_phcs'].fillna(0) + df['rhs_chcs'].fillna(0)
    phc_chc = phc_chc.where(df['rhs_phcs'].notna() | df['rhs_chcs'].notna(), pd.NA)
    add_var('infra_phc_chc_count', phc_chc, "Combined count of Primary and Community Health Centres (RHS), indicating basic healthcare coverage.")
    
    if 'pmbjp_kendra_count' in df.columns:
        add_var('infra_pmbjp_kendra_count', df['pmbjp_kendra_count'], "Count of Jan Aushadhi pharmacies, indicating access to affordable medicines.")
        
    # ── CLIMATE ──
    if 'csv_annual_rainfall_mm' in df.columns:
        add_var('climate_rainfall_annual_mm', df['csv_annual_rainfall_mm'], "Total annual rainfall (mm), baseline climate exposure.")
        add_var('climate_rainfall_volatility', df['csv_monthly_rainfall_std'], "Standard deviation of monthly rainfall, proxy for seasonal volatility and acute disease risk.")
        add_var('climate_rainfall_deviation_pct', df['xls_deviation_pct'], "Percentage deviation from normal rainfall (2012-2022), proxy for extreme weather shocks.")
        
    # ── Final Processing ──
    print(f"\nFinal slim table shape: {final_df.shape[0]} rows, {final_df.shape[1]} columns")
    
    missing_pct = (final_df.isnull().sum() / len(final_df)) * 100
    print("\nMissing % per selected column:")
    for col, pct in missing_pct.items():
        if col not in ['state_name', 'district_name', 'chronic_diabetes_source', 'chronic_hypertension_source']:
            print(f"  {col}: {pct:.1f}%")
            
    # Compute new completeness score (excluding strings and geography)
    numeric_cols = final_df.select_dtypes(include=['float64', 'int64', 'Float64', 'Int64']).columns
    final_df['data_completeness_score'] = (final_df[numeric_cols].notnull().sum(axis=1) / len(numeric_cols)) * 100
    print(f"\nAverage new data_completeness_score: {final_df['data_completeness_score'].mean():.1f}%")
    
    out_path = os.path.join(PROC_DIR, 'master_table_selected.csv')
    final_df.to_csv(out_path, index=False)
    print(f"✅ Saved to {out_path}")
    
    print("\nVariable Rationale (for PPT):")
    for j in justifications:
        print(j)

if __name__ == '__main__':
    main()
