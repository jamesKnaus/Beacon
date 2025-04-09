// Direct webhook handler for Notion
// This serverless function handles Notion webhooks and updates the knowledge base
// whenever changes are made to Notion pages
const { Client } = require('@notionhq/client');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Environment variables with fallback values
// These should be configured in Vercel project settings
const NOTION_TOKEN = process.env.NOTION_TOKEN || '';
const NOTION_PAGE_ID = process.env.NOTION_PAGE_ID || '';
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || '';
const KNOWLEDGE_BASE_DIR = process.env.KNOWLEDGE_BASE_DIR || 'knowledge_base';
const OUTPUT_FILE = process.env.OUTPUT_FILE || 'notion_content.json';

// Initialize Notion client with API token
const notion = new Client({
  auth: NOTION_TOKEN,
});

/**
 * Helper function to safely parse JSON
 * @param {any} body - The body to parse
 * @returns {Object} - The parsed object or empty object if parsing fails
 */
const parseBody = (body) => {
  if (!body) return {};
  if (typeof body === 'object') return body;
  try {
    return JSON.parse(body);
  } catch (e) {
    console.error('Error parsing body:', e);
    return {};
  }
};

// Log environment variables status (without revealing the actual values)
console.log('Environment variables status:');
console.log(`- NOTION_TOKEN: ${NOTION_TOKEN ? 'Set' : 'Not set'}`);
console.log(`- NOTION_PAGE_ID: ${NOTION_PAGE_ID ? 'Set' : 'Not set'}`);
console.log(`- WEBHOOK_SECRET: ${WEBHOOK_SECRET ? 'Set' : 'Not set'}`);

/**
 * Fetch content from Notion main page and all child pages
 * Updates the knowledge base JSON file with the latest content
 * @returns {Promise<boolean>} - Success or failure
 */
async function updateNotionContent() {
  console.log('Fetching and updating Notion content...');
  
  // Validate environment variables
  if (!NOTION_TOKEN || !NOTION_PAGE_ID) {
    console.error('Missing NOTION_TOKEN or NOTION_PAGE_ID. Cannot update content.');
    return false;
  }
  
  try {
    // Object to store all page content
    const knowledge_base = {};
    
    // Step 1: Get the main page and its title
    const page = await notion.pages.retrieve({ page_id: NOTION_PAGE_ID });
    const title = page.properties?.title?.title?.[0]?.plain_text || 'Beacon';
    console.log(`Retrieving main page: ${title}`);
    
    // Step 2: Get all blocks from the main page
    const blocks = await notion.blocks.children.list({ block_id: NOTION_PAGE_ID });
    
    // Step 3: Extract content and identify child pages
    const mainContent = [];
    const childPages = [];
    
    for (const block of blocks.results) {
      // Identify and store child pages for later processing
      if (block.type === 'child_page') {
        childPages.push({
          id: block.id,
          title: block.child_page.title
        });
      }
      
      // Extract text content from the block
      mainContent.push(extractTextFromBlock(block));
    }
    
    // Store main page content
    knowledge_base[title] = mainContent.join('\n\n');
    
    // Step 4: Process all child pages (first level only)
    console.log(`Found ${childPages.length} child pages`);
    for (const child of childPages) {
      try {
        // Get all blocks from the child page
        const childBlocks = await notion.blocks.children.list({ block_id: child.id });
        const childContent = [];
        
        // Extract text from each block
        for (const block of childBlocks.results) {
          childContent.push(extractTextFromBlock(block));
        }
        
        // Store child page content
        knowledge_base[child.title] = childContent.join('\n\n');
        console.log(`Retrieved: ${child.title}`);
      } catch (e) {
        console.error(`Error retrieving child page ${child.title}:`, e);
      }
    }
    
    // Step 5: Save content to knowledge base file
    const dirPath = path.join(process.cwd(), KNOWLEDGE_BASE_DIR);
    const filePath = path.join(dirPath, OUTPUT_FILE);
    
    try {
      // Create directory if it doesn't exist
      if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
      }
      
      // Write content to file
      fs.writeFileSync(filePath, JSON.stringify(knowledge_base, null, 2));
      console.log(`Saved updated content to ${filePath}`);
      return true;
    } catch (fileError) {
      console.error('Error saving content file:', fileError);
      return false;
    }
  } catch (error) {
    console.error('Error updating Notion content:', error);
    return false;
  }
}

/**
 * Extract readable text from a Notion block
 * @param {Object} block - The Notion block object
 * @returns {string} - Extracted text representation
 */
function extractTextFromBlock(block) {
  const blockType = block.type;
  if (!blockType) return '';
  
  const content = block[blockType];
  
  // Handle different block types with appropriate formatting
  if (blockType === 'paragraph') {
    return content.rich_text.map(text => text.plain_text).join('');
  } else if (blockType === 'heading_1') {
    return '# ' + content.rich_text.map(text => text.plain_text).join('');
  } else if (blockType === 'heading_2') {
    return '## ' + content.rich_text.map(text => text.plain_text).join('');
  } else if (blockType === 'heading_3') {
    return '### ' + content.rich_text.map(text => text.plain_text).join('');
  } else if (blockType === 'bulleted_list_item') {
    return '• ' + content.rich_text.map(text => text.plain_text).join('');
  } else if (blockType === 'numbered_list_item') {
    return '1. ' + content.rich_text.map(text => text.plain_text).join('');
  } else if (blockType === 'to_do') {
    const checked = content.checked ? '✓ ' : '☐ ';
    return checked + content.rich_text.map(text => text.plain_text).join('');
  } else if (blockType === 'code') {
    const code = content.rich_text.map(text => text.plain_text).join('');
    return `\`\`\`${content.language}\n${code}\n\`\`\``;
  } else if (blockType === 'child_page') {
    return `[Child Page: ${content.title}]`;
  } else if (blockType === 'child_database') {
    return `[Child Database: ${content.title}]`;
  } else if (blockType === 'divider') {
    return '---';
  } else if (blockType === 'callout') {
    const text = content.rich_text.map(t => t.plain_text).join('');
    const emoji = content.icon?.emoji || '';
    return `${emoji} ${text}`;
  }
  
  // Generic fallback for unsupported block types
  return `[${blockType} block]`;
}

/**
 * Main serverless function handler
 * Handles all HTTP requests to the webhook
 */
module.exports = async (req, res) => {
  // Setup CORS headers for cross-origin requests
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Notion-Webhook-Secret');
  
  // Handle preflight OPTIONS requests
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  console.log('Request received:', req.method, req.url);
  
  // ENDPOINT: Health check
  // URL: /api/health
  // Used to verify the service is running and environment variables are set
  if (req.method === 'GET' && (req.url === '/api/health' || req.url === '/health')) {
    console.log('Health check');
    
    // Test Notion API connection if token is provided
    let notionStatus = 'Not tested (no token)';
    if (NOTION_TOKEN) {
      try {
        // Try to retrieve users to validate token
        await notion.users.list();
        notionStatus = 'Connected';
      } catch (error) {
        notionStatus = `Error: ${error.message}`;
      }
    }
    
    return res.status(200).json({
      status: "healthy",
      message: "Notion webhook server is running",
      notion: notionStatus,
      environment: {
        notionToken: NOTION_TOKEN ? 'Set' : 'Not set',
        notionPageId: NOTION_PAGE_ID ? 'Set' : 'Not set',
        webhookSecret: WEBHOOK_SECRET ? 'Set' : 'Not set'
      }
    });
  }
  
  // ENDPOINT: Manual update trigger
  // URL: /api/trigger-update
  // Manually triggers an update of the knowledge base
  if (req.method === 'GET' && (req.url === '/api/trigger-update' || req.url === '/trigger-update')) {
    console.log('Manual update requested');
    
    const success = await updateNotionContent();
    if (success) {
      return res.status(200).json({
        status: "success",
        message: "Notion content updated successfully"
      });
    } else {
      return res.status(500).json({
        status: "error",
        message: "Failed to update Notion content"
      });
    }
  }
  
  // ENDPOINT: Home/index
  // URL: /
  // Provides basic info about available endpoints
  if (req.method === 'GET' && (req.url === '/' || req.url === '')) {
    console.log('Home page requested');
    return res.status(200).json({
      message: "Notion Webhook Server",
      endpoints: {
        webhook: "/api/webhook",
        health: "/api/health",
        update: "/api/trigger-update"
      }
    });
  }
  
  // ENDPOINT: Webhook receiver
  // URL: /api/webhook
  // Receives notifications from Notion when pages are updated
  if (req.method === 'POST' && (req.url === '/api/webhook' || req.url === '/webhook')) {
    console.log('Webhook request received');
    
    try {
      // Log full request details for debugging
      console.log('Headers:', JSON.stringify(req.headers));
      
      // Get the body from the request
      const body = parseBody(req.body);
      console.log('Request body:', JSON.stringify(body));
      
      // Handle verification request (required by Notion when setting up webhook)
      if (body.type === 'verification') {
        const verificationToken = body.verification_token;
        console.log(`Verification request with token: ${verificationToken}`);
        
        // Return the token to verify the webhook
        return res.status(200).json({ verification_token: verificationToken });
      }
      
      // Verify the webhook secret if provided
      if (WEBHOOK_SECRET) {
        const webhookSecret = req.headers['x-notion-webhook-secret'];
        if (webhookSecret !== WEBHOOK_SECRET) {
          console.error(`Invalid webhook secret received: ${webhookSecret}`);
          return res.status(401).json({ error: "Invalid webhook secret" });
        }
      }
      
      // Process normal webhook events (page updates, etc.)
      console.log(`Webhook event received: ${body.type || 'unknown'}`);
      
      // Update content when Notion changes occur
      // Note: We don't await this, so we can respond quickly to Notion
      updateNotionContent().then(success => {
        console.log('Content update completed:', success ? 'success' : 'failed');
      }).catch(err => {
        console.error('Error during content update:', err);
      });
      
      // Acknowledge receipt immediately (don't wait for content update to finish)
      return res.status(200).json({ success: true });
      
    } catch (error) {
      console.error(`Error processing webhook: ${error.message}`);
      return res.status(500).json({ error: error.message });
    }
  }
  
  // Default response for unmatched routes
  return res.status(404).json({ error: "Not found" });
}; 