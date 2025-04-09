import os
import re
import json
import sqlite3
from flask import Flask, render_template, request, jsonify, g, make_response, session
from dotenv import load_dotenv
import tiktoken
# Import without any proxies or custom settings
from openai import OpenAI

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'beacon-default-secret')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
FALLBACK_MODEL = 'gpt-3.5-turbo'  # Fallback to GPT-3.5 Turbo if GPT-4 is not available
MAX_BUDGET_DOLLARS = float(os.getenv('MAX_BUDGET_DOLLARS', '1.00'))

# Token pricing (approximate)
TOKEN_PRICING = {
    'gpt-4-turbo-preview': {
        'input': 0.00001,  # $0.01 per 1K tokens
        'output': 0.00003,  # $0.03 per 1K tokens
    },
    'gpt-3.5-turbo': {
        'input': 0.0000015,  # $0.0015 per 1K tokens
        'output': 0.000002,  # $0.002 per 1K tokens
    }
}

# Token counting functions
def num_tokens_from_string(string, model):
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def calculate_cost(input_tokens, output_tokens, model=OPENAI_MODEL):
    """Calculate cost of API call based on token count"""
    pricing = TOKEN_PRICING.get(model, TOKEN_PRICING['gpt-4-turbo-preview'])
    input_cost = input_tokens * pricing['input']
    output_cost = output_tokens * pricing['output']
    return input_cost + output_cost

# Domain knowledge 
NYC_REAL_ESTATE_KNOWLEDGE = {
    "investment_strategies": {
        "value": "Finding undervalued properties with potential for appreciation.",
        "cashflow": "Prioritizing rental income and positive cash flow.",
        "growth": "Long-term appreciation in developing or up-and-coming areas.",
        "luxury": "High-end properties in premium locations."
    },
    "boroughs": {
        "Manhattan": "Most densely populated, highest property values.",
        "Brooklyn": "Cultural diversity, rapidly appreciating neighborhoods.",
        "Queens": "Largest borough, mix of housing options.",
        "Bronx": "Most affordable, emerging investment opportunities.",
        "Staten Island": "Most suburban-like, lower density housing."
    },
    "popular_neighborhoods": {
        "Manhattan": ["Upper West Side", "Upper East Side", "Chelsea", "Greenwich Village", "Tribeca", "Harlem"],
        "Brooklyn": ["Williamsburg", "Park Slope", "DUMBO", "Brooklyn Heights", "Bushwick"],
        "Queens": ["Astoria", "Long Island City", "Forest Hills", "Flushing", "Jamaica"],
        "Bronx": ["Riverdale", "Mott Haven", "Fordham", "Pelham Bay"],
        "Staten Island": ["St. George", "Tottenville", "Great Kills"]
    },
    "property_types": {
        "Condo": "Individually owned units with less restrictions than co-ops.",
        "Co-op": "Shares in a corporation; typically lower prices but stricter rules.",
        "Townhouse": "Multi-story attached homes, often with rental income potential.",
        "Multi-family": "Buildings with multiple units, good for rental income.",
        "Single-family": "Standalone houses, less common in NYC except in outer boroughs."
    },
    "risk_levels": {
        "low": "Established neighborhoods with stable values and strong rental demand.",
        "medium": "Mix of established areas and up-and-coming neighborhoods.",
        "high": "Emerging neighborhoods with higher potential returns but greater uncertainty."
    }
}

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

# Database configuration
DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'beacon.db')

def get_db():
    """Connect to the database if not already connected"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection when app context ends"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Execute a database query and return results"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    """Insert data into the database"""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

# System prompt construction
def create_system_prompt():
    knowledge_json = json.dumps(NYC_REAL_ESTATE_KNOWLEDGE, indent=2)
    
    return f"""
    You are Beacon, an expert NYC real estate investment assistant. Your goal is to help users find investment properties in NYC that match their investment strategy and preferences.

    # IMPORTANT OBJECTIVES:
    1. Engage users in a natural, conversational way like a knowledgeable real estate agent would.
    2. Learn about their investment preferences (strategy, locations, property types, budget, risk tolerance).
    3. Guide the conversation toward collecting all necessary information to make property recommendations.
    4. Ultimately collect their email address to send them personalized property recommendations.
    5. Be helpful, professional, and knowledgeable about NYC real estate.

    # NYC REAL ESTATE KNOWLEDGE:
    {knowledge_json}

    # CONVERSATION GUIDELINES:
    - Start by introducing yourself and asking about their investment goals.
    - Ask about their preferred NYC boroughs and neighborhoods.
    - Inquire about property types they're interested in.
    - Ask about their budget range.
    - Assess their risk tolerance.
    - Suggest properties that match their criteria.
    - Offer to send personalized recommendations via email.
    - Always be conversational and natural, not scripted.
    - Use your knowledge of NYC real estate to provide valuable insights.

    # IMPORTANT INFORMATION TO COLLECT:
    - Investment strategy (value, cashflow, growth, luxury)
    - Preferred boroughs and neighborhoods
    - Property types of interest
    - Budget range
    - Risk tolerance

    # PROPERTY RECOMMENDATION:
    When you have enough information, suggest properties from our database. If the user expresses interest, offer to send more recommendations via email.

    # EMAIL COLLECTION:
    Once you've provided value and built rapport, ask for their email to send personalized property recommendations, market insights, and investment opportunities.

    Remember, your ultimate goal is to be helpful, provide real estate expertise, and collect the user's email to continue the relationship.
    """

# Conversation state management
def get_conversation_state():
    """Get or initialize the conversation state"""
    if 'conversation' not in session:
        session['conversation'] = {
            'messages': [],
            'token_count': {
                'input': 0,
                'output': 0
            },
            'cost': 0.0,
            'collected_info': {
                'investment_strategy': None,
                'boroughs': [],
                'neighborhoods': [],
                'property_types': [],
                'min_budget': None,
                'max_budget': None,
                'risk_tolerance': None,
                'name': None,
                'email': None
            }
        }
    return session['conversation']

def update_conversation_state(user_message, assistant_message, input_tokens, output_tokens):
    """Update the conversation state with new messages and token counts"""
    state = get_conversation_state()
    
    # Add messages
    state['messages'].append({'role': 'user', 'content': user_message})
    state['messages'].append({'role': 'assistant', 'content': assistant_message})
    
    # Update token counts
    state['token_count']['input'] += input_tokens
    state['token_count']['output'] += output_tokens
    
    # Update cost
    new_cost = calculate_cost(input_tokens, output_tokens)
    state['cost'] += new_cost
    
    # Save to session
    session['conversation'] = state
    
    return state

def is_within_budget():
    """Check if the conversation is still within budget"""
    state = get_conversation_state()
    return state['cost'] < MAX_BUDGET_DOLLARS

# Routes
@app.route('/')
def index():
    """Render the landing page"""
    return render_template('index.html')

@app.route('/api/test_openai')
def test_openai():
    """Test route to verify OpenAI API key is working"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            return jsonify({
                'success': False,
                'error': 'OpenAI API key is not set properly in .env file'
            })

        # Try a simple completion to test the API
        print(f"Testing OpenAI API with key starting with: {api_key[:5]}...")
        test_client = OpenAI(api_key=api_key)
        completion = test_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=10
        )
        return jsonify({
            'success': True,
            'message': completion.choices[0].message.content,
            'model': OPENAI_MODEL
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error testing OpenAI API: {str(e)}")
        print(f"Error details: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/chat')
def chat():
    """Render the chat interface"""
    return render_template('chat.html')

@app.route('/test')
def test():
    """Render test page"""
    return render_template('test.html')

# API Routes
@app.route('/api/message', methods=['POST'])
def handle_message():
    """Process incoming chat messages and return response"""
    data = request.json
    user_message = data.get('message', '')
    conversation_state = data.get('state', {})
    
    # Process message and generate response
    # This is a simple placeholder - we'll implement the full conversation logic later
    response = {
        'message': f"You said: {user_message}. This is where the chatbot response will go.",
        'state': conversation_state
    }
    
    return jsonify(response)

# New API endpoint for OpenAI chat
@app.route('/api/openai_chat', methods=['POST'])
def openai_chat():
    """Process chat messages through OpenAI API"""
    try:
        data = request.json
        user_message = data.get('message', '')
        user_info = data.get('user_info', {})
        
        print(f"Received message: {user_message}")
        
        # Get conversation state
        state = get_conversation_state()
        
        # Update collected info if provided
        if user_info:
            for key, value in user_info.items():
                if value and key in state['collected_info']:
                    state['collected_info'][key] = value
        
        # Check if we're over budget
        if not is_within_budget():
            return jsonify({
                'message': "I've enjoyed our conversation about NYC real estate investments, but I need to head to another client meeting now. Would you like to leave your email so I can send you some property recommendations that match what we've discussed?",
                'over_budget': True,
                'state': state
            })
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": create_system_prompt()}
        ]
        
        # Add conversation history
        for msg in state['messages']:
            messages.append({"role": msg['role'], "content": msg['content']})
        
        # Add user's current message
        messages.append({"role": "user", "content": user_message})
        
        # Count input tokens
        input_text = create_system_prompt() + "".join([m['content'] for m in state['messages']]) + user_message
        input_tokens = num_tokens_from_string(input_text, OPENAI_MODEL)
        
        # Try with the preferred model first, then fall back to GPT-3.5 if needed
        model_to_use = OPENAI_MODEL
        print(f"Calling OpenAI API with model: {model_to_use}")
        
        try:
            # Call OpenAI API with preferred model
            response = client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
        except Exception as model_error:
            print(f"Error with model {model_to_use}: {str(model_error)}")
            print(f"Falling back to {FALLBACK_MODEL}")
            model_to_use = FALLBACK_MODEL
            # Try with fallback model
            response = client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
        
        # Get assistant's response
        assistant_message = response.choices[0].message.content
        
        print(f"Received response from OpenAI using {model_to_use}")
        
        # Count output tokens
        output_tokens = num_tokens_from_string(assistant_message, model_to_use)
        
        # Update conversation state
        update_conversation_state(user_message, assistant_message, input_tokens, output_tokens)
        
        # Extract information from the message
        extracted_info = extract_info_from_message(user_message, assistant_message)
        if extracted_info:
            for key, value in extracted_info.items():
                if value and key in state['collected_info']:
                    state['collected_info'][key] = value
        
        return jsonify({
            'message': assistant_message,
            'state': state
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in OpenAI chat: {str(e)}")
        print(f"Error details: {error_details}")
        return jsonify({
            'message': "I'm sorry, I'm having trouble connecting with our property database right now. Could you please try again in a moment?",
            'error': str(e)
        }), 500

# Simple information extraction function
def extract_info_from_message(user_message, assistant_message):
    """Extract investment preferences from messages"""
    extracted = {}
    
    # Very basic extraction logic - in reality would be much more sophisticated
    user_lower = user_message.lower()
    
    # Extract investment strategy
    if 'value' in user_lower or 'undervalued' in user_lower:
        extracted['investment_strategy'] = 'value'
    elif 'cash flow' in user_lower or 'rental income' in user_lower:
        extracted['investment_strategy'] = 'cashflow'
    elif 'growth' in user_lower or 'appreciation' in user_lower:
        extracted['investment_strategy'] = 'growth'
    elif 'luxury' in user_lower or 'premium' in user_lower:
        extracted['investment_strategy'] = 'luxury'
    
    # Extract boroughs
    boroughs = []
    if 'manhattan' in user_lower:
        boroughs.append('Manhattan')
    if 'brooklyn' in user_lower:
        boroughs.append('Brooklyn')
    if 'queens' in user_lower:
        boroughs.append('Queens')
    if 'bronx' in user_lower:
        boroughs.append('Bronx')
    if 'staten island' in user_lower:
        boroughs.append('Staten Island')
    
    if boroughs:
        extracted['boroughs'] = boroughs
    
    # Extract email if present
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_message)
    if email_match:
        extracted['email'] = email_match.group(0)
    
    return extracted

@app.route('/api/submit_profile', methods=['POST'])
def submit_profile():
    """Save user investment profile and create user account"""
    data = request.json
    
    # Get conversation state to use collected info if not explicitly provided
    state = get_conversation_state()
    
    # Merge provided data with collected info
    for key, value in data.items():
        if value and key in state['collected_info']:
            state['collected_info'][key] = value
    
    try:
        # Save user info
        user_id = insert_db(
            "INSERT INTO users (name, email, newsletter_subscribed) VALUES (?, ?, ?)",
            (data.get('name') or state['collected_info']['name'], 
             data.get('email') or state['collected_info']['email'], 
             True)
        )
        
        # Save investment profile
        profile_id = insert_db(
            """INSERT INTO investment_profiles 
               (user_id, investment_strategy, boroughs, neighborhoods, 
                property_types, min_budget, max_budget, risk_tolerance) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, 
             data.get('investment_strategy') or state['collected_info']['investment_strategy'], 
             ','.join(data.get('boroughs', []) or state['collected_info']['boroughs']), 
             ','.join(data.get('neighborhoods', []) or state['collected_info']['neighborhoods']),
             ','.join(data.get('property_types', []) or state['collected_info']['property_types']),
             data.get('min_budget') or state['collected_info']['min_budget'],
             data.get('max_budget') or state['collected_info']['max_budget'],
             data.get('risk_tolerance') or state['collected_info']['risk_tolerance'])
        )
        
        return jsonify({'success': True, 'user_id': user_id, 'profile_id': profile_id})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_property_recommendation', methods=['POST'])
def get_property_recommendation():
    """Get property recommendation based on user profile"""
    data = request.json
    
    # Debug: Log received data
    print("API received data:", data)
    
    # Extract criteria
    investment_strategy = data.get('investment_strategy')
    boroughs = data.get('boroughs', [])
    property_types = data.get('property_types', [])
    
    # Get conversation state to use collected info if not explicitly provided
    state = get_conversation_state()
    if not investment_strategy and state['collected_info']['investment_strategy']:
        investment_strategy = state['collected_info']['investment_strategy']
    
    if not boroughs and state['collected_info']['boroughs']:
        boroughs = state['collected_info']['boroughs']
    
    if not property_types and state['collected_info']['property_types']:
        property_types = state['collected_info']['property_types']
    
    # Debug: Log what will be used for query
    print("Using for query:", {
        "investment_strategy": investment_strategy,
        "boroughs": boroughs,
        "property_types": property_types
    })
    
    # Build query based on criteria
    query = """
        SELECT * FROM sample_properties 
        WHERE investment_strategy = ?
    """
    params = [investment_strategy]
    
    # Add borough filter if specified
    if boroughs:
        borough_placeholders = ', '.join(['?' for _ in boroughs])
        query += f" AND borough IN ({borough_placeholders})"
        params.extend(boroughs)
    
    # Add property type filter if specified
    if property_types:
        type_placeholders = ', '.join(['?' for _ in property_types])
        query += f" AND property_type IN ({type_placeholders})"
        params.extend(property_types)
    
    # Debug: Log final query and params
    print("Final SQL query:", query)
    print("Query parameters:", params)
    
    # Get matching properties
    properties = query_db(query, params)
    
    # Convert to list of dicts for JSON serialization
    property_list = [dict(prop) for prop in properties]
    
    # Debug: Log results
    print("Query returned", len(property_list), "properties")
    
    # Return first match or empty if none found
    if property_list:
        return jsonify(property_list[0])
    else:
        return jsonify({'error': 'No matching properties found'}), 404

if __name__ == '__main__':
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    # Check if database exists, if not initialize it
    if not os.path.exists(DATABASE):
        from database.init_db import init_db
        init_db()
    
    # Run the app on all network interfaces with port 8080 instead of 5000
    app.run(debug=True, host='0.0.0.0', port=8080)
