# Supabase Setup Instructions for Real Estate Database

This guide provides step-by-step instructions to set up your Supabase database with real estate property data.

## Step 1: Prepare Your Data

Make sure your Excel data is cleaned and formatted correctly:

```bash
python clean_re_data.py
```

This will:
- Clean and format the data from the Excel files
- Create JSON and CSV exports in the `cleaned_data` directory
- Generate a Supabase schema file

## Step 2: Create the Database Schema in Supabase

You need to manually create the database schema in Supabase:

1. **Go to your Supabase dashboard:**
   - [https://app.supabase.com/project/pjtrzatzvtoeexrdsfsl](https://app.supabase.com/project/pjtrzatzvtoeexrdsfsl)

2. **Create the properties table:**
   - Click on "SQL Editor" in the left sidebar
   - Click "New query"
   - Copy and paste the following SQL (FIXED version that resolves the "WITH CHECK expression" error):

```sql
-- Enable the necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
```

> **NOTE:** This fixed version removes the Row Level Security (RLS) policies that were causing the "only WITH CHECK expression allowed for INSERT" error. If you need RLS policies, we can add them separately after the table is created correctly.

3. **Click "Run" to execute the SQL**

## Step 3: Upload the Data Using the API

After creating the database schema, upload the data using the Python script:

```bash
python upload_data.py
```

This script will:
- Connect to your Supabase project using the credentials in `.env`
- Check if the properties table exists
- Upload the cleaned data in small batches
- Handle errors and provide progress updates

## Step 4: Verify the Data

After uploading the data, verify it was uploaded correctly:

```bash
python verify_data.py
```

This will:
- Check the total number of records
- Show sample properties from Manhattan and Brooklyn
- Display the highest-value property
- Calculate basic statistics on the data

## Step 5: Use the API to Query the Data

Start the Flask API server to access your real estate data:

```bash
python property_api.py
```

This will start a server at http://localhost:5001 with these endpoints:

- `GET /api/properties` - Get properties based on query parameters
- `GET /api/properties/{property_id}` - Get a specific property by ID
- `POST /api/mcp/property-query` - Process natural language queries

## Step 6: Test the LLM Integration

To test the integration with the LLM:

```bash
python llm_property_integration.py
```

This will start a conversational interface where you can ask questions about properties in the database.

## Troubleshooting

If you encounter issues:

1. **Table Creation Errors:**
   - The "only WITH CHECK expression allowed for INSERT" error is caused by incorrect RLS policy syntax. Use the fixed SQL above which removes the problematic RLS policies.
   - If you need RLS policies, add them one by one after the table is created successfully.
   - Make sure you run the SQL commands in the Supabase SQL Editor
   - Check for syntax errors in the SQL

2. **Data Upload Errors:**
   - **Date/Time Format Errors**: If you see errors like "date/time field value out of range", this means the upload script is handling Unix timestamps that PostgreSQL can't parse. The fixed `upload_data.py` script now converts these timestamps to proper ISO date format.
   - **Data Type Errors**: If you see errors like "invalid input syntax for type integer", this means some fields (like `year_built`) need type conversion. The fixed script now properly converts float values to integers where needed.
   - Verify your Supabase credentials in the `.env` file
   - Try uploading with a smaller batch size
   - If you get permission errors, you may need to disable RLS or add appropriate policies

3. **API Connection Issues:**
   - Make sure the Flask API is running on port 5001
   - Check that your Supabase credentials are correct

4. **Data Format Issues:**
   - Run `clean_re_data.py` again to regenerate the cleaned data 