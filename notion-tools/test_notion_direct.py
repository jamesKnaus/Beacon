"""
Direct Notion API Test Script

This script directly uses the Notion API token and database ID
instead of loading from environment variables.
"""

import sys
from notion_client import Client
from notion_client.errors import APIResponseError

# Directly set the Notion API token and database ID
notion_token = "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"
notion_database_id = "19cf7b25-aad3-8011-b4c7-f88765dc4686"

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
    elif error.code == "object_not_found":
        print("\nThis could be due to:")
        print("1. Database ID is incorrect")
        print("2. Database has not been shared with your integration")
        print("   - Go to the database in Notion")
        print("   - Click '...' in the top-right corner")
        print("   - Select 'Add connections'")
        print("   - Find and select your integration")
    
    sys.exit(1)
    
except Exception as error:
    print(f"\nUnexpected error: {str(error)}")
    sys.exit(1)
    
print("\nAll tests completed successfully!") 