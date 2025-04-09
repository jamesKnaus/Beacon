"""
Notion Knowledge Base Integration for Beacon

This script demonstrates how to fetch content from a Notion page
and make it available for use in the Beacon chatbot.
"""

import os
import json
from dotenv import load_dotenv
from utils.notion_integration import NotionIntegration

# Load environment variables
load_dotenv()

# Check if Notion API key is configured
if not os.environ.get("NOTION_API_KEY"):
    print("Error: NOTION_API_KEY not found in environment variables")
    print("Please set NOTION_API_KEY in your .env file")
    exit(1)

# Check if Notion page ID is configured
if not os.environ.get("NOTION_PAGE_ID"):
    print("Error: NOTION_PAGE_ID not found in environment variables")
    print("Please set NOTION_PAGE_ID in your .env file")
    exit(1)

def main():
    print("Fetching content from Notion page...")
    
    try:
        # Initialize Notion integration
        notion = NotionIntegration()
        
        # Get page title
        page_title = notion.get_page_title()
        print(f"Page title: {page_title}")
        
        # Get page content
        page_content = notion.extract_page_text()
        
        # Save the content to a JSON file
        knowledge_base_dir = "knowledge_base"
        os.makedirs(knowledge_base_dir, exist_ok=True)
        
        output_file = os.path.join(knowledge_base_dir, "notion_content.json")
        with open(output_file, "w") as f:
            json.dump({page_title: page_content}, f, indent=2)
        
        print(f"Successfully extracted content from the Notion page")
        print(f"Content saved to {output_file}")
        
        # Preview some of the content
        print("\nContent preview:")
        preview_length = min(500, len(page_content))
        print(f"{page_content[:preview_length]}...")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main() 