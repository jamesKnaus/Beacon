#!/usr/bin/env python
"""
Notion Webhook Server

A lightweight server that listens for Notion webhooks and updates the local content
whenever changes are made in Notion.

For local use:
python notion_webhook_server.py

For cloud deployment (e.g., Render):
- Set the environment variables: NOTION_TOKEN, NOTION_PAGE_ID, WEBHOOK_SECRET, PORT
- The service will use these environment variables instead of hardcoded values
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from notion_client import Client
from notion_client.errors import APIResponseError
import sys

# Configuration from environment variables with fallbacks
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "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")
MAIN_PAGE_ID = os.environ.get("NOTION_PAGE_ID", "19cf7b25-aad3-8011-b4c7-f88765dc4686")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "knowledge_base")
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "notion_content.json")
LOG_FILE = os.environ.get("LOG_FILE", "notion_webhook.log")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "beacon_webhook_secret_83c271a4f5")
PORT = int(os.environ.get("PORT", 5002))  # Render assigns a PORT env variable

# Set up logging
# When deployed, log to stdout instead of a file
if "RENDER" in os.environ:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
else:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

# Initialize Flask app
app = Flask(__name__)

def extract_text_from_block(block):
    """Extract text content from a block"""
    block_type = block.get("type")
    if not block_type:
        return ""
    
    content = block.get(block_type, {})
    
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
    elif block_type == "callout":
        rich_text = content.get("rich_text", [])
        text = "".join([t.get("plain_text", "") for t in rich_text])
        emoji = content.get("icon", {}).get("emoji", "")
        return f"{emoji} {text}"
    elif block_type == "divider":
        return "---"
    
    return f"[{block_type} block]"

def get_notion_content():
    """Fetch content from Notion and return as a dictionary"""
    knowledge_base = {}
    
    try:
        # Initialize Notion client
        notion = Client(auth=NOTION_TOKEN)
        
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
        main_title = get_page_title(MAIN_PAGE_ID)
        logging.info(f"Retrieving main page: {main_title}")
        
        main_content, child_pages = get_page_content(MAIN_PAGE_ID)
        knowledge_base[main_title] = main_content
        
        # Process child pages (first level only)
        logging.info(f"Found {len(child_pages)} child pages")
        for child in child_pages:
            try:
                child_id = child["id"]
                child_title = child["title"]
                logging.debug(f"Retrieving: {child_title}")
                
                # Get content from child page
                child_content, _ = get_page_content(child_id)
                knowledge_base[child_title] = child_content
                
            except Exception as e:
                logging.error(f"Error retrieving child page {child_title}: {str(e)}")
        
        return knowledge_base
        
    except APIResponseError as error:
        logging.error(f"Notion API error: {error.code} - {error.body}")
        return None
    
    except Exception as error:
        logging.error(f"Unexpected error: {str(error)}")
        return None

def save_content(knowledge_base):
    """Save content to file and create backup if needed"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        
        # Check if content has changed
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r') as f:
                    old_content = json.load(f)
                
                if old_content == knowledge_base:
                    logging.info("Content unchanged, skipping save")
                    return True
                
                # Content has changed, create backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(OUTPUT_DIR, f"notion_content_backup_{timestamp}.json")
                logging.info(f"Content changed, backing up to {backup_path}")
                
                with open(output_path, 'r') as src:
                    with open(backup_path, 'w') as dst:
                        dst.write(src.read())
            except:
                logging.warning("Could not compare with existing content, saving anyway")
        
        # Save new content
        with open(output_path, "w") as f:
            json.dump(knowledge_base, f, indent=2)
        
        logging.info(f"Saved content from {len(knowledge_base)} pages to {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error saving content: {str(e)}")
        return False

def update_content():
    """Update the local content from Notion"""
    logging.info(f"Update triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get content from Notion
    knowledge_base = get_notion_content()
    
    if knowledge_base:
        # Save content
        save_content(knowledge_base)
        logging.info("Content update completed")
    else:
        logging.error("Failed to get content from Notion")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint that receives notifications from Notion"""
    # Check if this is a verification request
    payload = request.json
    if payload and payload.get('type') == 'verification':
        # This is a verification request, extract the verification token
        verification_token = payload.get('verification_token')
        logging.info(f"Received verification request with token: {verification_token}")
        # Return the token to verify ownership
        return jsonify({"verification_token": verification_token}), 200
    
    # Verify the webhook secret (if provided by Notion)
    webhook_secret = request.headers.get('X-Notion-Webhook-Secret')
    if webhook_secret != WEBHOOK_SECRET:
        logging.warning(f"Invalid webhook secret: {webhook_secret}")
        return jsonify({"status": "error", "message": "Invalid webhook secret"}), 401
    
    # Get the webhook payload
    
    # Log the webhook
    logging.info(f"Received webhook: {payload.get('type', 'unknown')}")
    
    # Update content based on webhook payload
    update_content()
    
    return jsonify({"status": "success"}), 200

@app.route('/trigger-update', methods=['GET'])
def trigger_update():
    """Manually trigger an update via HTTP"""
    update_content()
    return jsonify({"status": "success", "message": "Update triggered"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Create output directory if not exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Do an initial content update
    logging.info("Performing initial content update")
    update_content()
    
    # Start the webhook server
    logging.info(f"Starting webhook server on port {PORT}")
    print(f"Notion webhook server running on port {PORT}")
    print(f"Webhook URL: http://your-public-address:{PORT}/webhook")
    print(f"Health check: http://localhost:{PORT}/health")
    print(f"Manual update: http://localhost:{PORT}/trigger-update")
    
    # In production, use Render's PORT environment variable
    app.run(host='0.0.0.0', port=PORT) 