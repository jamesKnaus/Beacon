# Notion Webhook Server for Beacon

A serverless Node.js application that listens for Notion webhooks and automatically syncs content from Notion to the Beacon knowledge base.

## How It Works

This webhook server:
1. Receives notifications from Notion when pages are updated
2. Fetches the latest content from the main Beacon page
3. Retrieves content from all child pages
4. Saves the content to a JSON file for easy access by the Beacon application

## Endpoints

- `GET /` - Home page showing available endpoints
- `GET /api/health` - Health check that verifies the server is running and env variables are set
- `GET /api/trigger-update` - Manually trigger a content update
- `POST /api/webhook` - Webhook endpoint that Notion sends update notifications to

## Environment Variables

These variables should be set in your Vercel project settings:

| Variable | Description | Example |
|----------|-------------|---------|
| `NOTION_TOKEN` | Your Notion API token | `ntn_66490575571b...` |
| `NOTION_PAGE_ID` | The ID of your main Notion page | `19cf7b25-aad3-8011...` |
| `WEBHOOK_SECRET` | Secure string for verification | `beacon_webhook_secret_83c271a4f5` |
| `KNOWLEDGE_BASE_DIR` | Directory to store content | `knowledge_base` |
| `OUTPUT_FILE` | Filename for content JSON | `notion_content.json` |

## Deployment to Vercel

### Initial Deployment

1. Push this code to your GitHub repository:
   ```bash
   git add .
   git commit -m "Update Notion webhook handler"
   git push
   ```

2. In Vercel:
   - Connect to your GitHub repository
   - Add the environment variables listed above
   - Deploy the project

3. Once deployed, you'll get a URL like `https://your-webhook.vercel.app`

### Setting Up the Webhook in Notion

1. Go to [Notion integrations page](https://www.notion.so/my-integrations)
2. Select your integration
3. Under "Webhooks", click "Add new webhook"
4. Enter your Vercel URL: `https://your-webhook.vercel.app/api/webhook`
5. Enter the webhook secret (same as `WEBHOOK_SECRET` env variable)
6. Select events you want to be notified about (recommend: all page events)

## Testing the Webhook

1. Visit `https://your-webhook.vercel.app/api/health` to verify it's running
2. Visit `https://your-webhook.vercel.app/api/trigger-update` to manually sync content
3. Make a change in Notion and check if the content updates automatically

## Maintenance and Troubleshooting

### Updating the Code

1. Make changes to the files
2. Add and commit changes to git
3. Push to GitHub, Vercel will automatically redeploy

### Common Issues

- **Webhook verification fails**: Ensure webhook secret matches in both Notion and Vercel
- **Content not updating**: Check Vercel logs for error messages
- **Missing child pages**: The webhook retrieves one level of child pages only

### Vercel Logs

Always check Vercel logs for any errors when troubleshooting:
1. Go to your project in Vercel dashboard
2. Click "Functions" tab 
3. Select a function to view its logs

## File Structure

- `api/index.js` - Main webhook handler (serverless function)
- `vercel.json` - Vercel configuration
- `package.json` - Node.js dependencies

## What Gets Synchronized

The webhook syncs:
- The main Beacon page content
- All first-level child pages
- Content is formatted as markdown-like text
- Block types are preserved (headings, lists, code blocks, etc.)

## Security Notes

- Keep your Notion API token private
- The webhook secret ensures only authenticated requests are processed
- Vercel includes built-in HTTPS for secure connections 