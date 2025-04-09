
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
