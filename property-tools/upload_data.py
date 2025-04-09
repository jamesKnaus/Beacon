import os
import json
import time
import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def convert_timestamp_to_date(timestamp):
    """Convert Unix timestamp (milliseconds) to ISO date string"""
    if not timestamp or not isinstance(timestamp, (int, float)):
        return None
    
    try:
        # Convert milliseconds to seconds for datetime
        dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        return dt.strftime('%Y-%m-%d')
    except:
        return None

def cast_value(value, target_type):
    """Convert value to appropriate type, or None if not possible"""
    if value is None or (isinstance(value, float) and value != value):  # NaN check
        return None
    
    try:
        if target_type == int:
            if isinstance(value, float):
                return int(value)
            return value
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return str(value)
        else:
            return value
    except:
        return None

def upload_data():
    """Upload property data to Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found in .env file.")
        return
    
    print(f"Connecting to Supabase at {SUPABASE_URL}...")
    
    try:
        # Create Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase successfully!")
        
        # Check if properties table exists
        try:
            response = supabase.from_('properties').select('*', count='exact').limit(1).execute()
            count = response.count
            print(f"Properties table exists with {count} records.")
            
            if count > 0:
                proceed = input("Table already contains data. Do you want to continue uploading? (y/n): ")
                if proceed.lower() != 'y':
                    print("Upload canceled.")
                    return
        except Exception as e:
            print(f"Error checking properties table: {e}")
            print("Make sure you've created the table using the SQL in the Supabase dashboard.")
            return
        
        # Load data
        data_file = 'cleaned_data/all_properties.json'
        if not os.path.exists(data_file):
            print(f"Error: Data file {data_file} not found.")
            print("Run clean_re_data.py first to generate the cleaned data.")
            return
        
        print(f"Reading data from {data_file}...")
        with open(data_file, 'r') as f:
            all_properties = json.load(f)
        
        total_records = len(all_properties)
        print(f"Found {total_records} properties to upload.")
        
        # Upload in small batches for reliability
        batch_size = 10
        success_count = 0
        error_count = 0
        
        for i in range(0, total_records, batch_size):
            batch = all_properties[i:i+batch_size]
            end_idx = min(i+batch_size, total_records)
            
            print(f"Uploading batch {i+1}-{end_idx} of {total_records}...")
            
            try:
                # Clean the data - needed for Supabase compatibility
                clean_batch = []
                for prop in batch:
                    # Convert data types to match PostgreSQL expectations
                    clean_prop = {}
                    for key, value in prop.items():
                        if key == 'last_sale_date' or key == 'mls_listing_date':
                            clean_prop[key] = convert_timestamp_to_date(value)
                        elif key == 'year_built':
                            clean_prop[key] = cast_value(value, int)
                        elif isinstance(value, float) and value != value:  # NaN check
                            clean_prop[key] = None
                        else:
                            clean_prop[key] = value
                    
                    # Add to clean batch
                    clean_batch.append(clean_prop)
                
                # Upload to Supabase
                result = supabase.from_('properties').insert(clean_batch).execute()
                
                if result.data:
                    success_count += len(batch)
                    print(f"✅ Successfully uploaded batch {i+1}-{end_idx}.")
                else:
                    error_count += len(batch)
                    print(f"❌ Error in batch {i+1}-{end_idx}. No data returned.")
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                error_count += len(batch)
                print(f"❌ Error uploading batch {i+1}-{end_idx}: {e}")
                
                # Print more details for debugging
                if hasattr(e, 'code') and hasattr(e, 'message'):
                    print(f"  Details: code={e.code}, message={e.message}")
                
                # Print a sample of the problematic data for debugging
                print(f"  Sample data: {batch[0].get('year_built')}, type: {type(batch[0].get('year_built'))}")
                
                # Ask to continue if many errors
                if error_count > 50:
                    proceed = input("Many errors occurring. Continue uploading? (y/n): ")
                    if proceed.lower() != 'y':
                        print("Upload canceled.")
                        break
        
        print("\nUpload process completed!")
        print(f"Successful records: {success_count}")
        print(f"Failed records: {error_count}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    upload_data() 