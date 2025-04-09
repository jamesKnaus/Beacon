import pandas as pd
import sys
import json

# Read the Excel files
try:
    manhattan_df = pd.read_excel('re_data/manhattan _props.xlsx')
    brooklyn_df = pd.read_excel('re_data/brooklyn_absentee.xlsx')
    
    # Display the first few rows of each file
    print("MANHATTAN PROPERTIES STRUCTURE:")
    print("-------------------------------")
    print(f"Shape: {manhattan_df.shape}")
    print("Columns:")
    for col in manhattan_df.columns:
        print(f"- {col}")
    print("\nSample data (first 3 rows):")
    print(manhattan_df.head(3).to_string())
    
    print("\n\nBROOKLYN PROPERTIES STRUCTURE:")
    print("-------------------------------")
    print(f"Shape: {brooklyn_df.shape}")
    print("Columns:")
    for col in brooklyn_df.columns:
        print(f"- {col}")
    print("\nSample data (first 3 rows):")
    print(brooklyn_df.head(3).to_string())
    
except Exception as e:
    print(f"Error reading Excel files: {e}") 