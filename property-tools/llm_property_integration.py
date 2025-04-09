import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuration
API_BASE_URL = "http://localhost:5000"

def get_property_data(params=None):
    """Get property data from the API"""
    if not params:
        params = {}
    
    url = f"{API_BASE_URL}/api/properties"
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting properties: {response.status_code}")
        print(response.text)
        return None

def get_property_by_id(property_id):
    """Get a specific property by ID"""
    url = f"{API_BASE_URL}/api/properties/{property_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting property: {response.status_code}")
        print(response.text)
        return None

def process_nl_query(query):
    """Process a natural language query"""
    url = f"{API_BASE_URL}/api/mcp/property-query"
    response = requests.post(url, json={"query": query})
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error processing query: {response.status_code}")
        print(response.text)
        return None

def build_system_prompt(mcp_data=None):
    """Build a system prompt with MCP data"""
    base_prompt = """
    You are an expert NYC real estate investment advisor. Your goal is to provide helpful, accurate information about real estate properties in New York City based on the user's interests and the available property data.
    
    Use the provided property data to inform your responses. Only mention properties that are included in the context. Be specific about property details like location, price, size, and features.
    
    When discussing properties:
    - Provide address and neighborhood context
    - Mention key attributes like bedrooms, bathrooms, square footage
    - Discuss the estimated value and comparative market aspects
    - Relate properties to the user's stated preferences
    - Suggest similar properties when appropriate
    
    Keep your responses conversational but informative. Present property information clearly and in a way that helps the user make investment decisions.
    """
    
    if mcp_data:
        mcp_json = json.dumps(mcp_data, indent=2)
        return f"{base_prompt}\n\nProperty Context:\n{mcp_json}"
    
    return base_prompt

def generate_llm_response(user_message, conversation_history=None, mcp_data=None):
    """Generate a response using the OpenAI API with MCP context"""
    if conversation_history is None:
        conversation_history = []
    
    system_prompt = build_system_prompt(mcp_data)
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history
    for message in conversation_history:
        messages.append(message)
    
    # Add the user's message
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # or your preferred model
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I wasn't able to generate a response. Please try again."

def handle_property_conversation():
    """Handle a conversation about properties"""
    print("NYC Real Estate Investment Assistant")
    print("-----------------------------------")
    print("Ask me about properties in NYC, or type 'exit' to quit.\n")
    
    conversation_history = []
    mcp_data = None
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nThank you for using the NYC Real Estate Investment Assistant. Goodbye!")
            break
        
        # Process the user input and update MCP data
        if "show me" in user_input.lower() or "looking for" in user_input.lower() or "find" in user_input.lower():
            # This is likely a property search query
            nl_response = process_nl_query(user_input)
            if nl_response:
                mcp_data = {
                    "property_context": nl_response.get("property_context", {}),
                    "search_context": {
                        "query": nl_response.get("query"),
                        "filters": nl_response.get("extracted_parameters", {})
                    },
                    "conversation_memory": nl_response.get("conversation_memory", {})
                }
        elif "details" in user_input.lower() and mcp_data and "properties" in mcp_data.get("property_context", {}):
            # User wants details about a specific property
            properties = mcp_data["property_context"]["properties"]
            if properties and len(properties) > 0:
                # Get details for the first property
                property_id = properties[0]["property_id"]
                property_detail = get_property_by_id(property_id)
                if property_detail:
                    mcp_data = property_detail
        
        # Add the user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Generate a response
        assistant_response = generate_llm_response(user_input, conversation_history, mcp_data)
        
        print(f"\nAssistant: {assistant_response}")
        
        # Add the assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
        # Limit conversation history to prevent context length issues
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]

if __name__ == "__main__":
    # Make sure the Flask API is running before starting this script
    print("Checking if the property API is running...")
    try:
        requests.get(f"{API_BASE_URL}/api/properties", params={"limit": 1})
        print("API is running. Starting conversation...")
        handle_property_conversation()
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the API at {API_BASE_URL}")
        print("Please make sure to run 'python property_api.py' first.") 