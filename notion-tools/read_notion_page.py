"""
Notion Page Reader

This script reads content from a Notion page (not a database)
and demonstrates how to access page content.
"""

import sys
import json
import os
from notion_client import Client
from notion_client.errors import APIResponseError

# Directly set the Notion API token and page ID
notion_token = "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"
page_id = "19cf7b25-aad3-8011-b4c7-f88765dc4686"

# Print diagnostic information
print(f"Reading Notion page...")
print(f"Page ID: {page_id}")

try:
    # Initialize the Notion client
    notion = Client(auth=notion_token)
    
    # Test connection
    me = notion.users.me()
    print(f"Connected as: {me.get('name', 'Unknown user')}")
    
    # Retrieve the page
    print(f"\nRetrieving page information...")
    page = notion.pages.retrieve(page_id=page_id)
    
    # Try to get the page title
    title = "Untitled"
    if "properties" in page and "title" in page["properties"]:
        title_elements = page["properties"]["title"].get("title", [])
        if title_elements:
            title = "".join([text.get("plain_text", "") for text in title_elements])
    
    print(f"Page title: {title}")
    
    # Get the page content (blocks)
    print(f"\nRetrieving page content...")
    blocks = notion.blocks.children.list(block_id=page_id)
    
    # Process blocks
    all_blocks = blocks.get("results", [])
    print(f"Found {len(all_blocks)} blocks on the page")
    
    # Extract text content
    print("\nPage content:")
    print("--------------------------------------------------")
    
    def extract_text_from_block(block):
        """Extract text content from a block"""
        block_type = block.get("type")
        if not block_type:
            return ""
        
        # Get the block content
        content = block.get(block_type, {})
        
        # Handle different block types
        if block_type == "paragraph":
            rich_text = content.get("rich_text", [])
            return "".join([text.get("plain_text", "") for text in rich_text])
        
        elif block_type == "heading_1":
            rich_text = content.get("rich_text", [])
            return "# " + "".join([text.get("plain_text", "") for text in rich_text])
        
        elif block_type == "heading_2":
            rich_text = content.get("rich_text", [])
            return "## " + "".join([text.get("plain_text", "") for text in rich_text])
        
        elif block_type == "heading_3":
            rich_text = content.get("rich_text", [])
            return "### " + "".join([text.get("plain_text", "") for text in rich_text])
        
        elif block_type == "bulleted_list_item":
            rich_text = content.get("rich_text", [])
            return "• " + "".join([text.get("plain_text", "") for text in rich_text])
        
        elif block_type == "numbered_list_item":
            rich_text = content.get("rich_text", [])
            return "1. " + "".join([text.get("plain_text", "") for text in rich_text])
        
        elif block_type == "to_do":
            rich_text = content.get("rich_text", [])
            checked = "✓ " if content.get("checked") else "☐ "
            return checked + "".join([text.get("plain_text", "") for text in rich_text])
        
        elif block_type == "code":
            rich_text = content.get("rich_text", [])
            language = content.get("language", "")
            code = "".join([text.get("plain_text", "") for text in rich_text])
            return f"```{language}\n{code}\n```"
        
        return f"[{block_type} block]"
    
    # Extract and print text from each block
    page_content = []
    for block in all_blocks:
        text = extract_text_from_block(block)
        if text:
            print(text)
            page_content.append(text)
    
    print("--------------------------------------------------")
    
    # Save the page content to a JSON file
    output_dir = "knowledge_base"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "notion_content.json")
    with open(output_file, "w") as f:
        json.dump({title: "\n\n".join(page_content)}, f, indent=2)
    
    print(f"\nSaved page content to {output_file}")
    
except APIResponseError as error:
    print(f"\nError with Notion API: {error.code}")
    print(f"Error details: {error.body}")
    sys.exit(1)
    
except Exception as error:
    print(f"\nUnexpected error: {str(error)}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 