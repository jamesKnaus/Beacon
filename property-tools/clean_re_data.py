import pandas as pd
import numpy as np
import json
import os

# Create output directory if it doesn't exist
os.makedirs('cleaned_data', exist_ok=True)

# Read the Excel files
print("Reading Excel files...")
manhattan_df = pd.read_excel('re_data/manhattan _props.xlsx')
brooklyn_df = pd.read_excel('re_data/brooklyn_absentee.xlsx')

# Define essential columns for the MVP
essential_columns = [
    'Property Address',
    'Property City',
    'Property State',
    'Property Zip',
    'Property County',
    'Property Type Detail',
    'Bedroom Count',
    'Bathroom Count',
    'Total Building Area Square Feet',
    'Lot Size Square Feet',
    'Year Built',
    'Estimated Value',
    'Last Sale Price',
    'Last Sale Date',
    'Zoning Code',
    'Total Assessed Value',
    'Mls Status',
    'Mls Listing Date',
    'Mls Listing Amount'
]

# Function to clean and process each dataframe
def clean_properties_data(df, borough):
    # Select only essential columns that exist in the dataframe
    available_columns = [col for col in essential_columns if col in df.columns]
    cleaned_df = df[available_columns].copy()
    
    # Add borough column
    cleaned_df['Borough'] = borough
    
    # Clean and standardize data
    # Replace NaN values with None for better JSON compatibility
    cleaned_df = cleaned_df.replace({np.nan: None})
    
    # Convert numeric columns to appropriate types
    numeric_columns = [
        'Bedroom Count', 'Bathroom Count', 
        'Total Building Area Square Feet', 'Lot Size Square Feet',
        'Year Built', 'Estimated Value', 'Last Sale Price', 'Total Assessed Value',
        'Mls Listing Amount'
    ]
    
    for col in numeric_columns:
        if col in cleaned_df.columns:
            # Convert to float first to handle any string values
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
    
    # Format date columns
    date_columns = ['Last Sale Date', 'Mls Listing Date']
    for col in date_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
    
    # Extract neighborhood from address if possible
    # This is a simplified approach - for a production system, 
    # you might want to use a geocoding service
    
    # Generate a unique ID for each property
    cleaned_df['property_id'] = range(1, len(cleaned_df) + 1)
    
    # Move property_id to the first column
    cols = cleaned_df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('property_id')))
    cleaned_df = cleaned_df[cols]
    
    # Rename columns to be more database-friendly (lowercase, underscores)
    cleaned_df.columns = [col.lower().replace(' ', '_') for col in cleaned_df.columns]
    
    return cleaned_df

# Clean the data
print("Cleaning Manhattan properties data...")
manhattan_cleaned = clean_properties_data(manhattan_df, "Manhattan")

print("Cleaning Brooklyn properties data...")
brooklyn_cleaned = clean_properties_data(brooklyn_df, "Brooklyn")

# Combine the data
all_properties = pd.concat([manhattan_cleaned, brooklyn_cleaned], ignore_index=True)

# Reset the property_id to ensure it's unique across the combined dataset
all_properties['property_id'] = range(1, len(all_properties) + 1)

# Export cleaned data to CSV and JSON for easy import to Supabase
print("Exporting cleaned data...")
manhattan_cleaned.to_csv('cleaned_data/manhattan_properties.csv', index=False)
manhattan_cleaned.to_json('cleaned_data/manhattan_properties.json', orient='records')

brooklyn_cleaned.to_csv('cleaned_data/brooklyn_properties.csv', index=False)
brooklyn_cleaned.to_json('cleaned_data/brooklyn_properties.json', orient='records')

all_properties.to_csv('cleaned_data/all_properties.csv', index=False)
all_properties.to_json('cleaned_data/all_properties.json', orient='records')

# Print summary statistics
print("\nData Cleaning Complete!")
print(f"Manhattan properties: {len(manhattan_cleaned)}")
print(f"Brooklyn properties: {len(brooklyn_cleaned)}")
print(f"Total properties: {len(all_properties)}")

# Print sample of cleaned data
print("\nSample of cleaned data (first 3 rows):")
print(all_properties.head(3).to_string())

# Create a schema.sql file for Supabase
supabase_schema = """
-- Enable the necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Create the properties table
CREATE TABLE properties (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  property_id INTEGER,
  property_address TEXT,
  property_city TEXT,
  property_state TEXT,
  property_zip TEXT,
  property_county TEXT,
  property_type_detail TEXT,
  bedroom_count NUMERIC,
  bathroom_count NUMERIC,
  total_building_area_square_feet NUMERIC,
  lot_size_square_feet NUMERIC,
  year_built INTEGER,
  estimated_value NUMERIC,
  last_sale_price NUMERIC,
  last_sale_date DATE,
  zoning_code TEXT,
  total_assessed_value NUMERIC,
  mls_status TEXT,
  mls_listing_date DATE,
  mls_listing_amount NUMERIC,
  borough TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on the borough for faster queries
CREATE INDEX idx_properties_borough ON properties (borough);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_properties_updated_at
BEFORE UPDATE ON properties
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create RLS (Row Level Security) policies
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read property data
CREATE POLICY "Anyone can read properties"
ON properties FOR SELECT
USING (true);

-- Only authenticated users with specific permissions can modify data
CREATE POLICY "Only authorized users can insert properties"
ON properties FOR INSERT
TO authenticated
WITH CHECK (auth.uid() IN (
  SELECT id FROM auth.users
  WHERE auth.email() IN (SELECT email FROM admin_users)
));

CREATE POLICY "Only authorized users can update properties"
ON properties FOR UPDATE
TO authenticated
USING (auth.uid() IN (
  SELECT id FROM auth.users
  WHERE auth.email() IN (SELECT email FROM admin_users)
))
WITH CHECK (auth.uid() IN (
  SELECT id FROM auth.users
  WHERE auth.email() IN (SELECT email FROM admin_users)
));
"""

with open('cleaned_data/supabase_schema.sql', 'w') as f:
    f.write(supabase_schema)

print("\nCreated Supabase schema file at cleaned_data/supabase_schema.sql") 