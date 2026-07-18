import pandas as pd
import geopandas as gpd
import os

def main():
    print("Loading geographic data...")
    
    # Setup paths
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../raw_data'))
    proc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../processed_data'))
    os.makedirs(proc_dir, exist_ok=True)
    
    # Load SHRID names
    shrid_path = os.path.join(raw_dir, '01_geography', 'shrid_loc_names.csv')
    shrid_df = pd.read_csv(shrid_path, dtype={'shrid2': str})
    
    # Extract pc11_state_id and pc11_district_id from shrid2
    # Format: 11-SS-DDD-subdist-town_village
    shrid_df['pc11_state_id'] = shrid_df['shrid2'].str.split('-').str[1]
    shrid_df['pc11_district_id'] = shrid_df['shrid2'].str.split('-').str[2]
    
    # Get unique district mapping from shrid
    master_districts = shrid_df[['pc11_state_id', 'pc11_district_id', 'state_name', 'district_name']].drop_duplicates().copy()
    master_districts = master_districts.dropna(subset=['pc11_state_id', 'pc11_district_id'])
    
    # Load GPKG
    gpkg_path = os.path.join(raw_dir, '01_geography', 'district.gpkg')
    gpkg_df = gpd.read_file(gpkg_path)
    
    gpkg_districts = pd.DataFrame(gpkg_df.drop(columns='geometry'))
    
    # Standardize names
    master_districts['state_name'] = master_districts['state_name'].str.upper().str.strip()
    master_districts['district_name'] = master_districts['district_name'].str.upper().str.strip()
    gpkg_districts['district_name'] = gpkg_districts['district_name'].str.upper().str.strip()
    
    # Merge them on the unique PC11 IDs
    master_geography = pd.merge(
        master_districts, 
        gpkg_districts, 
        on=['pc11_state_id', 'pc11_district_id'], 
        suffixes=('_shrid', '_gpkg'), 
        how='outer'
    )
    
    # Diagnostics
    missing_state = master_geography['state_name'].isnull().sum()
    missing_shrid_dist = master_geography['district_name_shrid'].isnull().sum()
    missing_gpkg_dist = master_geography['district_name_gpkg'].isnull().sum()
    
    # Resolve names: Use SHRID name primarily, fallback to GPKG name
    master_geography['district_name'] = master_geography['district_name_shrid'].fillna(master_geography['district_name_gpkg'])
    
    # Hardcode missing state names for specific known gaps
    master_geography.loc[master_geography['pc11_state_id'] == '07', 'state_name'] = 'DELHI'
    master_geography.loc[(master_geography['pc11_state_id'] == '27') & (master_geography['pc11_district_id'] == '519'), 'state_name'] = 'MAHARASHTRA'
    
    master_geography['state_name'] = master_geography['state_name'].fillna('UNKNOWN_STATE')
    
    # Final cleanup
    master_geography = master_geography[['pc11_state_id', 'pc11_district_id', 'state_name', 'district_name']].drop_duplicates()
    master_geography = master_geography.sort_values(by=['pc11_state_id', 'pc11_district_id'])
    
    print("-" * 50)
    print("GEOGRAPHY LOAD REPORT")
    print("-" * 50)
    print(f"Total Unique Districts: {len(master_geography)}")
    print(f"Districts missing state name (in SHRID): {missing_state}")
    print(f"Districts in GPKG but missing in SHRID: {missing_shrid_dist}")
    print(f"Districts in SHRID but missing in GPKG: {missing_gpkg_dist}")
    
    dup_ids = master_geography.duplicated(subset=['pc11_state_id', 'pc11_district_id']).sum()
    if dup_ids > 0:
        print(f"WARNING: {dup_ids} duplicate PC11 ID combinations found!")
        
    dup_names = master_geography.duplicated(subset=['state_name', 'district_name']).sum()
    if dup_names > 0:
        print(f"WARNING: {dup_names} duplicate District Names found (within same state)!")
        
    # Save output
    out_path = os.path.join(proc_dir, 'geography_master.csv')
    master_geography.to_csv(out_path, index=False)
    
    print("-" * 50)
    print("SAMPLE ROWS (First 5):")
    print(master_geography.head(5).to_string(index=False))
    print("-" * 50)
    print(f"Saved master list to: {out_path}")

if __name__ == '__main__':
    main()
