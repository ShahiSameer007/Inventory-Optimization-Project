import pandas as pd
import numpy as np
import os

# --- 1. Load and Aggregate Data ---
FILE_PATH = "D:\PSOE_Project\datasets\Retail-Inventory.csv"
OUTPUT_FILE_PATH = "D:\PSOE_Project\datasets\psoe_data_cleaned.csv"

try:
    df_raw = pd.read_csv(FILE_PATH)
except FileNotFoundError:
    print(f"Error: Source file '{FILE_PATH}' not found. Please ensure it is in the same directory.")
    # Exiting gracefully if the source file isn't there
    exit()

# Aggregate the raw data to one row per product:
# - AVG_UNIT_SALES is used as the base for the Reorder Quantity.
# - The last recorded QUANTITY_ON_HAND is used as the Current Stock.
df_grouped = df_raw.groupby('PRODUCT_ID').agg(
    PRODUCT_NAME=('PRODUCT_NAME', 'first'),
    AVG_UNIT_SALES=('UNIT_SALES', 'mean'),  
    CURRENT_STOCK=('QUANTITY_ON_HAND', 'last') 
).reset_index()


# --- 2. Simulation of Financial Parameters (COST and PRICE) ---

# Define the simulated financial structure for each product type.
# We need these to calculate profit and cost for the DAA.
simulation_map = {
    'Berry Juice': {'UNIT_PRICE': 4.50, 'PROFIT_MARGIN_PERC': 0.40},  # Price $4.50, Cost $2.70
    'Mango Drink': {'UNIT_PRICE': 3.00, 'PROFIT_MARGIN_PERC': 0.35},  # Price $3.00, Cost $1.95
    'Lemonade':    {'UNIT_PRICE': 2.50, 'PROFIT_MARGIN_PERC': 0.30},
    'Water Bottle': {'UNIT_PRICE': 1.50, 'PROFIT_MARGIN_PERC': 0.25},
    'Diet Soda':   {'UNIT_PRICE': 2.00, 'PROFIT_MARGIN_PERC': 0.30},
    'Cola':        {'UNIT_PRICE': 2.00, 'PROFIT_MARGIN_PERC': 0.35},
    'Energy Drink': {'UNIT_PRICE': 5.00, 'PROFIT_MARGIN_PERC': 0.50},
    'Coffee Beans': {'UNIT_PRICE': 15.00, 'PROFIT_MARGIN_PERC': 0.60},
    'Tea Bags':    {'UNIT_PRICE': 8.00, 'PROFIT_MARGIN_PERC': 0.45}
}

# Add the simulated UNIT_PRICE and PROFIT_MARGIN to the DataFrame
df_grouped['UNIT_PRICE'] = df_grouped['PRODUCT_NAME'].map(lambda x: simulation_map.get(x, {}).get('UNIT_PRICE', 1.00))
df_grouped['PROFIT_MARGIN'] = df_grouped['PRODUCT_NAME'].map(lambda x: simulation_map.get(x, {}).get('PROFIT_MARGIN_PERC', 0.20))

# Calculate UNIT_COST (The 'Weight' in the DAA)
# COST = PRICE * (1 - MARGIN)
df_grouped['UNIT_COST'] = df_grouped['UNIT_PRICE'] * (1 - df_grouped['PROFIT_MARGIN'])

# Calculate LOW_STOCK_THRESHOLD (Set threshold as 30% of average sales)
df_grouped['LOW_STOCK_THRESHOLD'] = np.ceil(df_grouped['AVG_UNIT_SALES'] * 0.30)

# --- 3. Finalize and Save ---

# Rename columns to reflect their new purpose and match the DB schema
df_final = df_grouped.rename(columns={
    'AVG_UNIT_SALES': 'REORDER_QUANTITY'
})

# Select and order the final required columns
df_final = df_final[['PRODUCT_ID', 'PRODUCT_NAME', 'CURRENT_STOCK', 'REORDER_QUANTITY', 'UNIT_COST', 'UNIT_PRICE', 'LOW_STOCK_THRESHOLD']]

# Save the final cleaned data to a new CSV file
df_final.to_csv(OUTPUT_FILE_PATH, index=False, float_format='%.2f')

print(f"✅ Success: Data cleaning and simulation complete.")
print(f"File saved to: {os.path.abspath(OUTPUT_FILE_PATH)}")
print("\n--- New Data Snapshot ---")
print(df_final.head().to_markdown(index=False))

# Optional check: show data types
print("\n--- New Data Types ---")
df_final.info()
