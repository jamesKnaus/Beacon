# Beacon - NYC Real Estate Intelligence Platform

## Overview
Beacon is an AI-powered real estate intelligence platform focused on NYC residential properties. It provides conversational interface for property search, investment analysis, and content management through Notion integration.

## Components

### 1. Real Estate Property Tools
Tools for processing, analyzing, and accessing NYC real estate property data.

- **Data Processing**: Clean and process Excel real estate data
- **Database Integration**: Upload/manage data with Supabase
- **API**: Flask-based API for property queries
- **LLM Integration**: Conversational interface for property search

### 2. Notion Integration
Three approaches for integrating Notion content with Claude:

- **Background Sync**: Scheduled polling that syncs content hourly
- **Claude Desktop Direct**: Native integration for Claude Desktop
- **Webhook Server**: Immediate updates when Notion content changes (recommended)

### 3. Web Application
Conversational chatbot that onboards users, captures preferences, and delivers property recommendations.

- **Interactive UI**: Modern, responsive interface
- **User Profiles**: Save investment criteria
- **Newsletter System**: Email updates with personalized recommendations

## Project Structure

```
.
├── notion-webhook/           # Webhook server for real-time Notion updates
├── notion-tools/             # Notion API integration utilities
├── property-tools/           # Real estate data processing tools
│   ├── cleaned_data/         # Processed property data
│   ├── re_data/              # Raw property data
│   └── sql/                  # Database schemas
├── utils/                    # Shared utility functions
├── docs/                     # Documentation
├── database/                 # Database models and initialization
├── scripts/                  # Utility scripts
├── templates/                # HTML templates
├── static/                   # CSS, JavaScript, and images
└── models/                   # Data models
```

## Setup Instructions

See individual component directories for specific setup instructions:

- **Real Estate Tools**: See `property-tools/README.md`
- **Notion Webhook**: See `notion-webhook/README.md`
- **Notion Background Sync**: See `notion-tools/README.md`

## Main Configuration

Create a `.env` file with your API keys and configuration:

```
# OpenAI API
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo

# Supabase credentials
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here

# Notion API credentials
NOTION_API_KEY=your_key_here
NOTION_PAGE_ID=your_page_id_here
```

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables in `.env`
4. Choose the appropriate Notion integration approach
5. Initialize the database: `python database/init_db.py`
6. Run the application: `python app.py`

## License

This project is licensed under the MIT License.
