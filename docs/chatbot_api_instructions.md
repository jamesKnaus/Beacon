# Real Estate Data API Chatbot Integration Guide

This guide explains how to use the real estate property API with a chatbot to interact with your Supabase database of Manhattan and Brooklyn properties.

## Setting Up the Environment

1. Make sure your Supabase database is properly set up with property data:
   ```bash
   python verify_data.py
   ```
   This should show that data has been successfully uploaded.

2. Start the Flask API server:
   ```bash
   python property_api.py
   ```
   This will start the server on http://localhost:5001

3. In a separate terminal, run the LLM integration script:
   ```bash
   python llm_property_integration.py
   ```
   This will start the chatbot interface.

## API Endpoints for Direct Integration

If you want to build your own chatbot integration, use these endpoints:

### 1. Get Properties with Filters
```
GET /api/properties
```

Query parameters:
- `borough`: Filter by borough (Manhattan or Brooklyn)
- `min_price`: Minimum estimated value
- `max_price`: Maximum estimated value
- `min_bedrooms`: Minimum number of bedrooms
- `min_bathrooms`: Minimum number of bathrooms
- `property_type`: Filter by property type
- `min_sqft`: Minimum square footage
- `max_year_built`: Maximum year built
- `sort_by`: Field to sort by (default: estimated_value)
- `sort_direction`: Sort direction (asc or desc)
- `limit`: Maximum number of results (default: 10)

Example:
```
GET /api/properties?borough=Manhattan&min_price=1000000&min_bedrooms=2&sort_by=estimated_value&sort_direction=desc
```

### 2. Get Property by ID
```
GET /api/properties/{property_id}
```

Example:
```
GET /api/properties/1234
```

### 3. Natural Language Query API
```
POST /api/mcp/property-query
```

Request body:
```json
{
  "query": "Show me luxury properties in Manhattan with at least 3 bedrooms"
}
```

## Example Chatbot Interactions

Here are some example queries you can try with the chatbot:

1. General property searches:
   - "Show me properties in Manhattan"
   - "What are the most expensive properties in Brooklyn?"
   - "Find properties with at least 3 bedrooms"
   - "Show me properties under $2 million"

2. Specific property features:
   - "What properties have the largest square footage?"
   - "Show me properties built before 1950"
   - "Find properties with at least 2 bathrooms in Manhattan"

3. Investment-focused queries:
   - "What's the average property value in Brooklyn?"
   - "Which neighborhoods in Manhattan have the highest value properties?"
   - "Compare property values between Manhattan and Brooklyn"
   - "What's the price per square foot for properties in Manhattan?"

4. Follow-up questions:
   - "Tell me more about that first property"
   - "What similar properties are available?"
   - "How does that compare to the average in the area?"

## Understanding the Response Format

The API returns data in a Model Context Protocol (MCP) format, which structures the data for better LLM interaction. The main components are:

1. `property_context`: Contains information about properties
   - `current_property`: Details about a specific property
   - `similar_properties`: List of properties similar to the current one

2. `search_context`: Contains search parameters and filters

3. `conversation_memory`: Tracks property mentions and user questions

## Troubleshooting

1. If the API server doesn't start:
   - Check that your Supabase credentials are correct in the `.env` file
   - Make sure all required Python packages are installed

2. If queries return no results:
   - Verify data was uploaded correctly with `verify_data.py`
   - Check that your filter parameters aren't too restrictive

3. If the chatbot gives inaccurate responses:
   - The LLM may not have access to all properties due to API limits
   - Try more specific queries or adjust the parameters

## Extension Ideas

1. Create a web interface for the chatbot
2. Add geographic visualization of properties on a map
3. Implement more advanced filters like neighborhood or property features
4. Add user accounts to save favorite properties and searches 