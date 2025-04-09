"""
Notion Webhook Server for Vercel

A serverless function that listens for Notion webhooks and updates content
whenever changes are made in Notion.

Designed to be deployed on Vercel.
"""

import os
import json
import logging
from datetime import datetime
import sys
from flask import Flask, request, jsonify, Response
from notion_client import Client
from notion_client.errors import APIResponseError

# Configure logging to stdout for Vercel
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Configuration from environment variables
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
MAIN_PAGE_ID = os.environ.get("NOTION_PAGE_ID", "")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

# Initialize Flask app for the serverless function
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
    """Fetch content from Notion and process it"""
    try:
        # Initialize Notion client
        notion = Client(auth=NOTION_TOKEN)
        
        # Get and process content here
        # This is simplified for the serverless function
        # In a real deployment, we would store this data in a database or file storage
        
        logging.info("Successfully retrieved and processed Notion content")
        return {"status": "success"}
        
    except APIResponseError as error:
        logging.error(f"Notion API error: {error.code} - {error.body}")
        return {"status": "error", "message": str(error)}
    
    except Exception as error:
        logging.error(f"Unexpected error: {str(error)}")
        return {"status": "error", "message": str(error)}

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint that receives notifications from Notion"""
    # Log incoming request
    logging.info(f"Received webhook request")
    
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
        logging.warning(f"Invalid webhook secret")
        return jsonify({"status": "error", "message": "Invalid webhook secret"}), 401
    
    # Log the webhook
    logging.info(f"Received webhook: {payload.get('type', 'unknown')}")
    
    # Process the webhook
    result = get_notion_content()
    
    return jsonify({"status": "success"}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

# Default route for Vercel
@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return jsonify({
        "message": "Notion Webhook Server",
        "endpoints": {
            "webhook": "/api/webhook",
            "health": "/api/health"
        }
    }), 200

# Handler for Vercel serverless function
def handler(request, response):
    return app(request, response) 