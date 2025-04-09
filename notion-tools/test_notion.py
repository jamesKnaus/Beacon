"""
Simple Notion API Test Script

This script tests the basic connection to the Notion API
and provides detailed error reporting.
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

# Load environment variables
load_dotenv()

# Get the Notion API token from environment variables
notion_token = os.environ.get("NOTION_API_KEY")
notion_database_id = os.environ.get("NOTION_DATABASE_ID")

# Print diagnostic information
print(f"Testing Notion API connection...")
print(f"Token format: {notion_token[:4]}...{notion_token[-4:]}")
print(f"Database ID: {notion_database_id}")

try:
    # Initialize the Notion client
    notion = Client(auth=notion_token)
    
    # Test a simple API call (users.me endpoint)
    print("\nTrying to get current user information...")
    response = notion.users.me()
    print(f"Success! Connected as: {response.get('name', 'Unknown user')}")
    
    print("\nTrying to retrieve database information...")
    database = notion.databases.retrieve(database_id=notion_database_id)
    print(f"Success! Database title: {database.get('title', [{}])[0].get('plain_text', 'Untitled')}")
    
    # Try querying the database
    print("\nTrying to query the database...")
    query_result = notion.databases.query(database_id=notion_database_id)
    result_count = len(query_result.get("results", []))
    print(f"Success! Found {result_count} items in the database.")
    
except APIResponseError as error:
    print(f"\nError with Notion API: {error.code}")
    print(f"Error details: {error.body}")
    
    if error.code == "unauthorized":
        print("\nThis could be due to:")
        print("1. Invalid token (check that you're using the correct token)")
        print("2. Token format issue (make sure it's copied correctly)")
        print("3. Integration permissions (make sure you've shared the database with your integration)")
    
    sys.exit(1)
    
except Exception as error:
    print(f"\nUnexpected error: {str(error)}")
    sys.exit(1)
    
print("\nAll tests completed successfully!") 