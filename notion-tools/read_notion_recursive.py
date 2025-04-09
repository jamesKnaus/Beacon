"""
Recursive Notion Page Reader

This script reads content from a Notion page and its child pages,
retrieving content from one level of nested pages.
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
print(f"Reading Notion page and child pages...")
print(f"Main Page ID: {page_id}")

# Knowledge base to store all content
knowledge_base = {}

try:
    # Initialize the Notion client
    notion = Client(auth=notion_token)
    
    # Test connection
    me = notion.users.me()
    print(f"Connected as: {me.get('name', 'Unknown user')}")
    
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
        
        elif block_type == "child_page":
            return f"[Child Page: {content.get('title', 'Untitled')}]"
            
        elif block_type == "child_database":
            return f"[Child Database: {content.get('title', 'Untitled')}]"
        
        return f"[{block_type} block]"
    
    def get_page_title(page_id):
        """Get the title of a Notion page"""
        page = notion.pages.retrieve(page_id=page_id)
        
        title = "Untitled"
        if "properties" in page and "title" in page["properties"]:
            title_elements = page["properties"]["title"].get("title", [])
            if title_elements:
                title = "".join([text.get("plain_text", "") for text in title_elements])
        
        return title
    
    def get_page_content(page_id):
        """Get content from a page and return as text"""
        blocks = notion.blocks.children.list(block_id=page_id)
        all_blocks = blocks.get("results", [])
        
        # Extract and collect text from each block
        page_content = []
        child_pages = []
        
        for block in all_blocks:
            # Store child page IDs for later processing
            if block.get("type") == "child_page":
                child_id = block.get("id")
                child_title = block.get("child_page", {}).get("title", "Untitled Child Page")
                child_pages.append({"id": child_id, "title": child_title})
                
            # Extract text from this block
            text = extract_text_from_block(block)
            if text:
                page_content.append(text)
        
        return "\n\n".join(page_content), child_pages
    
    # Process main page
    print("\nRetrieving main page...")
    main_title = get_page_title(page_id)
    print(f"Main page title: {main_title}")
    
    main_content, child_pages = get_page_content(page_id)
    knowledge_base[main_title] = main_content
    
    # Process child pages (first level only)
    print(f"\nFound {len(child_pages)} child pages. Retrieving content...")
    for i, child in enumerate(child_pages, 1):
        try:
            child_id = child["id"]
            child_title = child["title"]
            print(f"  {i}. Retrieving: {child_title} ({child_id})")
            
            # Get content from child page
            child_content, grandchild_pages = get_page_content(child_id)
            knowledge_base[child_title] = child_content
            
            print(f"     Contains {len(grandchild_pages)} sub-pages")
        except Exception as e:
            print(f"     Error retrieving child page: {str(e)}")
    
    # Save all content to a JSON file
    output_dir = "knowledge_base"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "notion_recursive_content.json")
    with open(output_file, "w") as f:
        json.dump(knowledge_base, f, indent=2)
    
    print(f"\nSaved content from main page and {len(knowledge_base)-1} child pages to {output_file}")
    
    # Print a summary of what was retrieved
    print("\nContent summary:")
    for title, content in knowledge_base.items():
        content_preview = content[:100].replace("\n", " ")
        print(f"• {title}: {content_preview}...")
    
except APIResponseError as error:
    print(f"\nError with Notion API: {error.code}")
    print(f"Error details: {error.body}")
    sys.exit(1)
    
except Exception as error:
    print(f"\nUnexpected error: {str(error)}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 