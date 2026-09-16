import pandas as pd
from conn import engine

query = """
SELECT 
    t.transaction_id, 
    s.Market, 
    s.State, 
    t.Commodity, 
    t.Modal_Price, 
    t.Arrival_Date
FROM Transaction t
INNER JOIN Supplier s ON t.supplier_id = s.supplier_id
LIMIT 1000;
"""

df_final = pd.read_sql(query, con=engine)

print(f"Total columns retrieved: {df_final.shape[1]}")
print(df_final['State'].unique())
print(df_final.head(100000)['Arrival_Date'].unique())