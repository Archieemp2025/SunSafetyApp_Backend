import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. LOAD SECRETS
# Looking one level up (../) because the script is inside the db_init/ folder
load_dotenv(dotenv_path="../.env")

# Get the DB URL from the environment variable
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    print("Error: DATABASE_URL not found in .env file.")
    print("Check if your .env is in the root folder and DATABASE_URL is correct.")
    exit(1)

engine = create_engine(DB_URL)

def run_etl():
    print("Starting Secure Full ETL with 10-Year Age Aggregation...")
    
    # Path to the file in the root directory (../)
    file_path = "../Data/aihw_cancer_incidence_data.xlsx"
    sheet_name = "Table S1a.1"
    
    try:
        # 2. EXTRACT
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=5)
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return

    # Clean column names (standardizing spaces and removing newlines)
    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    rate_col = 'Age-specific rate (per 100,000)'

    # 3. TRANSFORM
    # Filter for Melanoma and exclude 'All ages combined' to prevent double counting
    df = df[(df['Cancer group/site'] == 'Melanoma of the skin') & 
            (df['Age group (years)'] != 'All ages combined') &
            (df['Year'] >= 2007)
            ].copy()
    
    # THE FIX: Standardize the dashes
    # # This replaces the long En Dash  with a standard hyphen (-)
    # This avoids red lines in VS Code!
    df['Age group (years)'] = df['Age group (years)'].str.replace(u'\u2013', '-', regex=True).str.strip()
    
    # Ensure numeric types
    df['Count'] = pd.to_numeric(df['Count'], errors='coerce').fillna(0)
    df[rate_col] = pd.to_numeric(df[rate_col], errors='coerce').fillna(0.0)

    # Map 5-year brackets to 10-year brackets
    age_map = {
        '00-04': '00-09', '05-09': '00-09',
        '10-14': '10-19', '15-19': '10-19',
        '20-24': '20-29', '25-29': '20-29',
        '30-34': '30-39', '35-39': '30-39',
        '40-44': '40-49', '45-49': '40-49',
        '50-54': '50-59', '55-59': '50-59',
        '60-64': '60-69', '65-69': '60-69',
        '70-74': '70-79', '75-79': '70-79',
        '80-84': '80-89', '85-89': '80-89',
        '90+': '90+'
    }
    
    df['Age group (10yr)'] = df['Age group (years)'].map(age_map)

    # Aggregate: Sum the counts and Average the rates
    final_df = df.groupby(['Year', 'Sex', 'Cancer group/site', 'Age group (10yr)']).agg({
        'Count': 'sum',
        rate_col: 'mean'
    }).reset_index()

    # 4. LOAD
    with engine.connect() as conn:
        print("Refreshing Database Tables...")
        # Clear existing data to avoid duplicates
        conn.execute(text("TRUNCATE TABLE CANCER_INCIDENCE_STAT RESTART IDENTITY CASCADE"))
        
        # Ensure 'Melanoma of the skin' exists in Lookup
        conn.execute(text("INSERT INTO CANCER_TYPE (cancer_name, icd10_code) VALUES ('Melanoma of the skin', 'C43') ON CONFLICT (cancer_name) DO UPDATE SET icd10_code = EXCLUDED.icd10_code"))
        
        # Populate Lookup Tables
        for sex in final_df['Sex'].unique():
            if pd.notna(sex):
                conn.execute(text("INSERT INTO SEX (sex_label) VALUES (:l) ON CONFLICT DO NOTHING"), {"l": sex})
        
        for age in final_df['Age group (10yr)'].unique():
            if pd.notna(age):
                conn.execute(text("INSERT INTO AGE_GROUP (age_bracket) VALUES (:b) ON CONFLICT DO NOTHING"), {"b": age})
        
        conn.commit()

        print(f"Loading {len(final_df)} aggregated records into PostgreSQL...")
        cancer_id = conn.execute(text("SELECT cancer_id FROM CANCER_TYPE WHERE cancer_name = 'Melanoma of the skin'")).scalar()

        for _, row in final_df.iterrows():
            sex_id = conn.execute(text("SELECT sex_id FROM SEX WHERE sex_label = :l"), {"l": row['Sex']}).scalar()
            age_id = conn.execute(text("SELECT age_group_id FROM AGE_GROUP WHERE age_bracket = :b"), {"b": row['Age group (10yr)']}).scalar()
            
            conn.execute(text("""
                INSERT INTO CANCER_INCIDENCE_STAT (year, count, incidence_rate, cancer_id, sex_id, age_group_id)
                VALUES (:yr, :cnt, :rate, :c_id, :s_id, :a_id)
            """), {
                "yr": int(row['Year']),
                "cnt": int(row['Count']),
                "rate": float(row[rate_col]),
                "c_id": cancer_id,
                "s_id": sex_id,
                "a_id": age_id
            })
        
        conn.commit()
    
    print("Success! Your aggregated 10-year data is securely loaded.")

if __name__ == "__main__":
    run_etl()