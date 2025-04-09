"""
Notion Search Script

This script searches for content in your Notion workspace
to help identify available databases.
"""

import sys
from notion_client import Client
from notion_client.errors import APIResponseError

# Directly set the Notion API token
notion_token = "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"

# Print diagnostic information
print(f"Searching Notion workspace...")

try:
    # Initialize the Notion client
    notion = Client(auth=notion_token)
    
    # Test connection
    me = notion.users.me()
    print(f"Connected as: {me.get('name', 'Unknown user')}")
    
    # Search for "Beacon" in the workspace
    print("\nSearching for 'Beacon' content...")
    search_results = notion.search(query="Beacon")
    
    # Process results
    results = search_results.get("results", [])
    print(f"Found {len(results)} items matching 'Beacon'")
    
    for i, item in enumerate(results, 1):
        object_type = item.get("object")
        item_id = item.get("id")
        
        # Get title based on object type
        title = "Untitled"
        if object_type == "page":
            if "properties" in item and "title" in item["properties"]:
                title_elements = item["properties"]["title"].get("title", [])
                if title_elements:
                    title = "".join([text.get("plain_text", "") for text in title_elements])
            elif "title" in item:
                title_elements = item.get("title", [])
                if title_elements:
                    title = "".join([text.get("plain_text", "") for text in title_elements])
        elif object_type == "database":
            if "title" in item:
                title_elements = item.get("title", [])
                if title_elements:
                    title = "".join([text.get("plain_text", "") for text in title_elements])
        
        print(f"\n{i}. {object_type.upper()}: {title}")
        print(f"   ID: {item_id}")
        print(f"   URL: https://notion.so/{item_id.replace('-', '')}")
        
        # For databases, list properties
        if object_type == "database":
            print(f"   This is a database. You can use this ID in your .env file.")
            if "properties" in item:
                print(f"   Properties: {', '.join(item['properties'].keys())}")
    
    if not results:
        print("\nNo results found. Try searching for a different term.")
        print("You might need to create a database in your Notion workspace.")
    
except APIResponseError as error:
    print(f"\nError with Notion API: {error.code}")
    print(f"Error details: {error.body}")
    sys.exit(1)
    
except Exception as error:
    print(f"\nUnexpected error: {str(error)}")
    sys.exit(1) 