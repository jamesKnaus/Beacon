# Notion Webhook Server

A webhook server for Notion that keeps your content in sync. This server listens for webhooks from Notion and updates local content when changes occur.

## Features

- Receives notifications from Notion when content changes
- Responds to Notion's verification challenge
- Updates content immediately when changes are detected
- Can be deployed to Vercel for 24/7 operation
- Completely free to run

## Setup Options

### Option 1: Deploy to Vercel (Recommended)

For a 24/7 solution with a permanent URL, deploy to Vercel:

1. See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for complete instructions
2. Provides a permanent URL for Notion webhooks
3. Zero maintenance required

### Option 2: Run Locally

For testing or local development:

1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python notion_webhook_server.py`
3. Use a service like ngrok or localtunnel to expose your local server

## How it Works

1. Notion sends a webhook when content changes
2. The server verifies the webhook's authenticity
3. The server fetches the updated content from Notion
4. The content is saved for use by your application

## Configuration

Configure the server with environment variables:

- `NOTION_TOKEN`: Your Notion API token
- `NOTION_PAGE_ID`: Your main Notion page ID
- `WEBHOOK_SECRET`: A secure random string for webhook verification 