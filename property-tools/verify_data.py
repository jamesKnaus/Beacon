import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
import numpy as np

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def format_value(value, include_dollar=True, include_commas=True):
    """Safely format a value that might be None"""
    if value is None:
        return "Not available"
    
    if isinstance(value, (int, float)):
        if include_commas:
            formatted = f"{value:,.2f}"
        else:
            formatted = f"{value:.2f}"
            
        if include_dollar:
            return f"${formatted}"
        return formatted
    
    return str(value)

def verify_supabase_data():
    """Verify the data was uploaded correctly to Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found in .env file.")
        return
    
    print(f"Connecting to Supabase at {SUPABASE_URL}...")
    
    try:
        # Create Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase successfully!")
        
        # Get total count
        try:
            count_response = supabase.from_('properties').select('*', count='exact').limit(1).execute()
            count = count_response.count
            print(f"Found {count} total properties in the database.")
            
            if count == 0:
                print("No data found. Please run upload_data.py first.")
                return
        except Exception as e:
            print(f"Error checking property count: {e}")
            print("Make sure the properties table exists.")
            return
        
        # Check Manhattan properties
        manhattan_response = supabase.from_('properties').select('*').eq('borough', 'Manhattan').limit(5).execute()
        manhattan_count = len(manhattan_response.data)
        print(f"\nManhatten Properties ({manhattan_count} sample records):")
        for prop in manhattan_response.data:
            print(f"  - {prop.get('property_address')}: {format_value(prop.get('estimated_value'))}")
        
        # Check Brooklyn properties
        brooklyn_response = supabase.from_('properties').select('*').eq('borough', 'Brooklyn').limit(5).execute()
        brooklyn_count = len(brooklyn_response.data)
        print(f"\nBrooklyn Properties ({brooklyn_count} sample records):")
        for prop in brooklyn_response.data:
            print(f"  - {prop.get('property_address')}: {format_value(prop.get('estimated_value'))}")
        
        # Check property with highest value
        # Use IS NOT NULL filter to exclude properties with no estimated value
        highest_value_response = supabase.from_('properties').select('*').filter('estimated_value', 'not.is', 'null').order('estimated_value', desc=True).limit(1).execute()
        if highest_value_response.data:
            highest_prop = highest_value_response.data[0]
            print(f"\nHighest Value Property:")
            print(f"  Address: {highest_prop.get('property_address')}")
            print(f"  Borough: {highest_prop.get('borough')}")
            print(f"  Value: {format_value(highest_prop.get('estimated_value'))}")
            print(f"  Size: {format_value(highest_prop.get('total_building_area_square_feet'), include_dollar=False)} sq ft")
        
        # Data statistics
        print("\nCalculating data statistics...")
        
        # Get data to calculate statistics manually (since direct aggregates aren't working)
        value_data_response = supabase.from_('properties').select('estimated_value').filter('estimated_value', 'not.is', 'null').execute()
        
        if value_data_response.data:
            # Extract the values
            values = [p.get('estimated_value') for p in value_data_response.data if p.get('estimated_value') is not None]
            
            if values:
                min_price = min(values)
                max_price = max(values)
                avg_price = sum(values) / len(values)
                
                print(f"  Price Range: {format_value(min_price)} - {format_value(max_price)}")
                print(f"  Average Price: {format_value(avg_price)}")
                print(f"  Sample Size: {len(values)} properties with price data")
        
        # Borough distribution - we'll count records
        manhattan_count_response = supabase.from_('properties').select('*', count='exact').eq('borough', 'Manhattan').limit(1).execute()
        brooklyn_count_response = supabase.from_('properties').select('*', count='exact').eq('borough', 'Brooklyn').limit(1).execute()
        
        manhattan_total = manhattan_count_response.count
        brooklyn_total = brooklyn_count_response.count
        
        print("\nBorough Distribution:")
        print(f"  Manhattan: {manhattan_total} properties ({manhattan_total/count*100:.1f}%)")
        print(f"  Brooklyn: {brooklyn_total} properties ({brooklyn_total/count*100:.1f}%)")
        
        print("\nVerification complete. Data appears to be uploaded correctly.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_supabase_data() 