# Deploying Notion Webhook Server to Vercel

This guide explains how to deploy the Notion webhook server to Vercel for a persistent, always-on solution.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup) (the free tier is sufficient)
2. [GitHub account](https://github.com/signup) (to host the code)
3. Your Notion API credentials and page IDs

## Step 1: Push the Code to GitHub

1. Create a new GitHub repository
2. Push this code to your repository
   ```bash
   git init
   git add api/ vercel.json VERCEL_DEPLOYMENT.md
   git commit -m "Add Notion webhook server for Vercel"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

## Step 2: Set Up Environment Variables in Vercel

1. Go to the [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Import Project" or "New Project"
3. Select your GitHub repository
4. In the configuration step, add the following Environment Variables:
   - `NOTION_TOKEN`: Your Notion API token
   - `NOTION_PAGE_ID`: Your main Notion page ID
   - `WEBHOOK_SECRET`: A secure random string for webhook verification

## Step 3: Deploy

1. Complete the Vercel setup and click "Deploy"
2. Vercel will automatically build and deploy your webhook server
3. Once deployed, you'll get a URL like `https://your-project.vercel.app`

## Step 4: Set Up the Webhook in Notion

1. Go to your [Notion integrations page](https://www.notion.so/my-integrations)
2. Select your integration
3. Under "Webhooks", click "Add new webhook"
4. Enter your Vercel URL plus the webhook endpoint: `https://your-project.vercel.app/api/webhook`
5. Enter the same webhook secret you used in your Vercel environment variables
6. Select the events you want to be notified about

## Testing the Deployment

1. Visit `https://your-project.vercel.app/api/health` to check if the server is running
2. Make a change to your Notion page to trigger a webhook notification
3. Check the Vercel logs to see if the webhook was received and processed

## Troubleshooting

- **Webhook Verification Failed**: Make sure the webhook secret is exactly the same in both Notion and your Vercel environment variables
- **Content Not Updating**: Check the Vercel logs for any error messages
- **Deploy Errors**: Ensure all dependencies are listed in `api/requirements.txt`

## Benefits of Vercel Deployment

- Free hosting with generous limits
- Always-on service
- Automatic scaling
- Global CDN distribution
- CI/CD built-in (automatic deployments when you push to GitHub) 