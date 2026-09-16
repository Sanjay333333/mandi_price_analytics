import os

import requests
import pandas as pd
from conn import engine

url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
api_key = os.getenv("API_KEY")

params = {
    "api-key": api_key,
    "format": "json",
    "limit": 50,
    "filters[state.keyword]": "Tamil Nadu"
}

headers = {
    "User-Agent": "AgritechDataPipeline/1.0"
}

print("Fetching live market data...")
response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    data = response.json()
    df_live = pd.DataFrame(data['records'])
    print(f"Retrieved {len(df_live)} raw rows from API.")
    
    # 1. Fetch the existing supplier lookup table from MySQL
    query = "SELECT supplier_id, Market, State FROM Supplier"
    df_suppliers = pd.read_sql(query, con=engine)
    
    # 2. Standardize API columns to match MySQL schema exactly
    df_live = df_live.rename(columns={
        "market": "Market",
        "state": "State",
        "commodity": "Commodity",
        "min_price": "Min_Price",
        "max_price": "Max_Price",
        "modal_price": "Modal_Price",
        "arrival_date": "Arrival_Date"
    })
    
    # 3. Merge to attach the numeric supplier_id based on Market and State
    df_mapped = pd.merge(df_live, df_suppliers, on=['Market', 'State'], how='inner')
    
    # 4. Filter down to ONLY the columns that exist in the Transaction table
    df_insert = df_mapped[['supplier_id', 'Commodity', 'Min_Price', 'Max_Price', 'Modal_Price', 'Arrival_Date']].copy()
    
    # 4.5 Convert the DD/MM/YYYY text into SQL-ready YYYY-MM-DD format
    df_insert['Arrival_Date'] = pd.to_datetime(df_insert['Arrival_Date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

    print(f"Successfully mapped {len(df_insert)} live rows to internal supplier IDs.")
    print(df_insert.head())
    
    # 5. THE FINAL STEP: Append the live data to the database!
    df_insert.to_sql("Transaction", con=engine, if_exists="append", index=False)
    print("✅ Live data successfully appended to MySQL Transaction table!")