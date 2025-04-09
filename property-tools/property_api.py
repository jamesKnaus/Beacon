import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client
import random
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Create Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# If Supabase credentials are not set, we'll use local JSON file as a fallback
USE_LOCAL_DATA = not (SUPABASE_URL and SUPABASE_KEY) or os.getenv('USE_LOCAL_DATA', 'false').lower() == 'true'
LOCAL_DATA_FILE = 'cleaned_data/all_properties.json'

def get_supabase_client():
    """Get Supabase client if credentials are available"""
    if not USE_LOCAL_DATA:
        try:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            return None
    return None

supabase = get_supabase_client()

def load_local_data():
    """Load property data from local JSON file"""
    try:
        with open(LOCAL_DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading local data: {e}")
        return []

local_properties = load_local_data() if USE_LOCAL_DATA else None

# Utility functions
def format_property_for_mcp(property_data):
    """Format a property record for the MCP structure"""
    return {
        "property_id": str(property_data.get('property_id')),
        "address": property_data.get('property_address'),
        "city": property_data.get('property_city'),
        "state": property_data.get('property_state'),
        "zip": property_data.get('property_zip'),
        "borough": property_data.get('borough'),
        "property_type": property_data.get('property_type_detail'),
        "bedrooms": property_data.get('bedroom_count'),
        "bathrooms": property_data.get('bathroom_count'),
        "building_sqft": property_data.get('total_building_area_square_feet'),
        "lot_sqft": property_data.get('lot_size_square_feet'),
        "year_built": property_data.get('year_built'),
        "estimated_value": property_data.get('estimated_value'),
        "last_sale_price": property_data.get('last_sale_price'),
        "last_sale_date": str(property_data.get('last_sale_date')) if property_data.get('last_sale_date') else None
    }

def format_property_summary(property_data):
    """Format a property record as a summary for the MCP structure"""
    return {
        "property_id": str(property_data.get('property_id')),
        "address": property_data.get('property_address'),
        "borough": property_data.get('borough'),
        "estimated_value": property_data.get('estimated_value'),
        "bedrooms": property_data.get('bedroom_count'),
        "bathrooms": property_data.get('bathroom_count')
    }

def query_properties_from_supabase(params):
    """Query properties from Supabase based on parameters"""
    query = supabase.table('properties').select('*')
    
    # Apply filters
    if params.get('borough'):
        boroughs = params['borough'] if isinstance(params['borough'], list) else [params['borough']]
        query = query.in_('borough', boroughs)
    
    if params.get('min_price'):
        query = query.gte('estimated_value', params['min_price'])
    
    if params.get('max_price'):
        query = query.lte('estimated_value', params['max_price'])
    
    if params.get('min_bedrooms'):
        query = query.gte('bedroom_count', params['min_bedrooms'])
    
    if params.get('min_bathrooms'):
        query = query.gte('bathroom_count', params['min_bathrooms'])
    
    if params.get('property_type'):
        property_types = params['property_type'] if isinstance(params['property_type'], list) else [params['property_type']]
        query = query.in_('property_type_detail', property_types)
    
    if params.get('min_sqft'):
        query = query.gte('total_building_area_square_feet', params['min_sqft'])
    
    if params.get('max_year_built'):
        query = query.lte('year_built', params['max_year_built'])
    
    # Apply limit and sorting
    limit = params.get('limit', 10)
    query = query.limit(limit)
    
    sort_by = params.get('sort_by', 'estimated_value')
    sort_direction = params.get('sort_direction', 'desc')
    
    if sort_direction.lower() == 'desc':
        query = query.order(sort_by, desc=True)
    else:
        query = query.order(sort_by)
    
    # Execute query
    try:
        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Error querying Supabase: {e}")
        return []

def query_properties_from_local(params):
    """Query properties from local data based on parameters"""
    if not local_properties:
        return []
    
    # Start with all properties
    filtered_properties = local_properties.copy()
    
    # Apply filters
    if params.get('borough'):
        boroughs = params['borough'] if isinstance(params['borough'], list) else [params['borough']]
        filtered_properties = [p for p in filtered_properties if p.get('borough') in boroughs]
    
    if params.get('min_price'):
        filtered_properties = [p for p in filtered_properties if p.get('estimated_value') is not None and p.get('estimated_value') >= params['min_price']]
    
    if params.get('max_price'):
        filtered_properties = [p for p in filtered_properties if p.get('estimated_value') is not None and p.get('estimated_value') <= params['max_price']]
    
    if params.get('min_bedrooms'):
        filtered_properties = [p for p in filtered_properties if p.get('bedroom_count') is not None and p.get('bedroom_count') >= params['min_bedrooms']]
    
    if params.get('min_bathrooms'):
        filtered_properties = [p for p in filtered_properties if p.get('bathroom_count') is not None and p.get('bathroom_count') >= params['min_bathrooms']]
    
    if params.get('property_type'):
        property_types = params['property_type'] if isinstance(params['property_type'], list) else [params['property_type']]
        filtered_properties = [p for p in filtered_properties if p.get('property_type_detail') in property_types]
    
    if params.get('min_sqft'):
        filtered_properties = [p for p in filtered_properties if p.get('total_building_area_square_feet') is not None and p.get('total_building_area_square_feet') >= params['min_sqft']]
    
    if params.get('max_year_built'):
        filtered_properties = [p for p in filtered_properties if p.get('year_built') is not None and p.get('year_built') <= params['max_year_built']]
    
    # Apply sorting
    sort_by = params.get('sort_by', 'estimated_value')
    sort_direction = params.get('sort_direction', 'desc')
    
    reverse = sort_direction.lower() == 'desc'
    
    # Handle None values for sorting
    filtered_properties = sorted(
        filtered_properties,
        key=lambda x: (x.get(sort_by) is None, x.get(sort_by)),
        reverse=reverse
    )
    
    # Apply limit
    limit = params.get('limit', 10)
    return filtered_properties[:limit]

def find_similar_properties(property_id, limit=3):
    """Find similar properties to the given property"""
    # Get the target property
    target_property = None
    
    if USE_LOCAL_DATA:
        target_property = next((p for p in local_properties if str(p.get('property_id')) == str(property_id)), None)
    else:
        response = supabase.table('properties').select('*').eq('property_id', property_id).execute()
        if response.data:
            target_property = response.data[0]
    
    if not target_property:
        return []
    
    # Define criteria for similarity
    similarity_params = {
        'borough': target_property.get('borough'),
        'min_bedrooms': max(0, (target_property.get('bedroom_count') or 0) - 1),
        'min_bathrooms': max(0, (target_property.get('bathroom_count') or 0) - 1),
        'min_price': (target_property.get('estimated_value') or 0) * 0.7,
        'max_price': (target_property.get('estimated_value') or 0) * 1.3,
        'limit': limit + 1  # Get one extra to filter out the original property
    }
    
    # Query similar properties
    if USE_LOCAL_DATA:
        similar = query_properties_from_local(similarity_params)
    else:
        similar = query_properties_from_supabase(similarity_params)
    
    # Remove the target property from results
    similar = [p for p in similar if str(p.get('property_id')) != str(property_id)]
    
    # Return limited results
    return similar[:limit]

# API Routes
@app.route('/api/properties', methods=['GET'])
def get_properties():
    """Get properties based on query parameters"""
    # Extract parameters from query string
    params = {
        'borough': request.args.getlist('borough') or None,
        'min_price': float(request.args.get('min_price')) if request.args.get('min_price') else None,
        'max_price': float(request.args.get('max_price')) if request.args.get('max_price') else None,
        'min_bedrooms': float(request.args.get('min_bedrooms')) if request.args.get('min_bedrooms') else None,
        'min_bathrooms': float(request.args.get('min_bathrooms')) if request.args.get('min_bathrooms') else None,
        'property_type': request.args.getlist('property_type') or None,
        'min_sqft': float(request.args.get('min_sqft')) if request.args.get('min_sqft') else None,
        'max_year_built': int(request.args.get('max_year_built')) if request.args.get('max_year_built') else None,
        'sort_by': request.args.get('sort_by', 'estimated_value'),
        'sort_direction': request.args.get('sort_direction', 'desc'),
        'limit': int(request.args.get('limit', 10))
    }
    
    # Clean parameters, removing None values
    params = {k: v for k, v in params.items() if v is not None}
    
    # Query properties
    if USE_LOCAL_DATA:
        properties = query_properties_from_local(params)
    else:
        properties = query_properties_from_supabase(params)
    
    # Create MCP structure for response
    response = {
        "search_context": {
            "filters": {
                "borough": params.get('borough', []),
                "min_price": params.get('min_price'),
                "max_price": params.get('max_price'),
                "min_bedrooms": params.get('min_bedrooms'),
                "min_bathrooms": params.get('min_bathrooms'),
                "property_type": params.get('property_type', []),
                "min_sqft": params.get('min_sqft'),
                "max_year_built": params.get('max_year_built')
            },
            "sort_by": params.get('sort_by'),
            "sort_direction": params.get('sort_direction')
        },
        "properties": [format_property_for_mcp(p) for p in properties]
    }
    
    return jsonify(response)

@app.route('/api/properties/<property_id>', methods=['GET'])
def get_property(property_id):
    """Get a specific property by ID"""
    # Get property data
    property_data = None
    
    if USE_LOCAL_DATA:
        property_data = next((p for p in local_properties if str(p.get('property_id')) == str(property_id)), None)
    else:
        response = supabase.table('properties').select('*').eq('property_id', property_id).execute()
        if response.data:
            property_data = response.data[0]
    
    if not property_data:
        return jsonify({"error": "Property not found"}), 404
    
    # Find similar properties
    similar_properties = find_similar_properties(property_id)
    
    # Create MCP structure for response
    response = {
        "property_context": {
            "current_property": format_property_for_mcp(property_data),
            "similar_properties": [format_property_summary(p) for p in similar_properties]
        }
    }
    
    return jsonify(response)

@app.route('/api/mcp/property-query', methods=['POST'])
def property_query_mcp():
    """API endpoint that accepts natural language queries and returns property data in MCP format"""
    # Get request data
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query parameter"}), 400
    
    user_query = data['query']
    
    # Sample logic to extract search parameters from natural language query
    # In a real app, you would use an LLM to extract these parameters
    params = {}
    
    if 'manhattan' in user_query.lower():
        params['borough'] = ['Manhattan']
    elif 'brooklyn' in user_query.lower():
        params['borough'] = ['Brooklyn']
    
    if 'under 2 million' in user_query.lower():
        params['max_price'] = 2000000
    elif 'under 1 million' in user_query.lower():
        params['max_price'] = 1000000
    
    if 'at least 2 bedrooms' in user_query.lower():
        params['min_bedrooms'] = 2
    elif 'at least 3 bedrooms' in user_query.lower():
        params['min_bedrooms'] = 3
    
    # Query properties based on extracted parameters
    if USE_LOCAL_DATA:
        properties = query_properties_from_local(params)
    else:
        properties = query_properties_from_supabase(params)
    
    # If no specific filters were extracted, return a random sample
    if not params and properties:
        # Get a random sample
        random.shuffle(properties)
        properties = properties[:5]
    
    # Create MCP structure for response
    response = {
        "query": user_query,
        "extracted_parameters": params,
        "property_context": {
            "properties": [format_property_for_mcp(p) for p in properties]
        },
        "conversation_memory": {
            "property_mentions": [
                {
                    "property_id": str(p.get('property_id')),
                    "mention_count": 1,
                    "last_mentioned_at": datetime.now().isoformat()
                } for p in properties
            ],
            "user_questions": [user_query]
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    # Check if we can connect to Supabase or if we're using local data
    if USE_LOCAL_DATA:
        print(f"Running with local data from {LOCAL_DATA_FILE}")
        print(f"Found {len(local_properties) if local_properties else 0} properties in local data.")
    else:
        print(f"Connected to Supabase at {SUPABASE_URL}")
    
    # Run the Flask app
    app.run(debug=True, port=5000) 