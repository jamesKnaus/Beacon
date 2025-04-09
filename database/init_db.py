import sqlite3
import os
import sys

# Add parent directory to path so we can import from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'beacon.db')

def init_db():
    """Initialize the database with schema and sample data"""
    # Connect to database (will create if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read schema file
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
        schema = f.read()
    
    # Execute schema
    cursor.executescript(schema)
    
    # Insert sample properties data
    sample_properties = [
        # Manhattan properties
        ('The Hudson Residence', 'Luxury condominium with river views and high-end finishes', 'Manhattan', 'Upper West Side', 
         'Condo', 1950000, 2, 2.0, 1200, 'value', 4.2, 'medium', '/static/images/property1.jpg'),
        ('Greenwich Village Co-op', 'Pre-war co-op with character in prime location', 'Manhattan', 'Greenwich Village', 
         'Co-op', 1250000, 1, 1.0, 750, 'growth', 3.8, 'low', '/static/images/property2.jpg'),
        ('Tribeca Loft', 'Converted loft space with high ceilings and open floor plan', 'Manhattan', 'Tribeca', 
         'Condo', 3200000, 3, 2.5, 2200, 'luxury', 3.5, 'medium', '/static/images/property3.jpg'),
        
        # Brooklyn properties
        ('Williamsburg Townhouse', 'Renovated brownstone with rental unit in basement', 'Brooklyn', 'Williamsburg', 
         'Townhouse', 2750000, 4, 3.5, 2800, 'cashflow', 5.1, 'low', '/static/images/property4.jpg'),
        ('Park Slope Condo', 'Modern condo near Prospect Park with outdoor space', 'Brooklyn', 'Park Slope', 
         'Condo', 1450000, 2, 2.0, 1100, 'value', 4.5, 'low', '/static/images/property5.jpg'),
        ('Dumbo Loft', 'Industrial conversion with Manhattan views', 'Brooklyn', 'Dumbo', 
         'Condo', 1850000, 1, 1.5, 1300, 'growth', 4.8, 'medium', '/static/images/property6.jpg'),
        
        # Queens properties
        ('Astoria Multi-family', 'Three-unit building with stable rental income', 'Queens', 'Astoria', 
         'Multi-family', 1650000, 6, 3.0, 3200, 'cashflow', 6.2, 'medium', '/static/images/property7.jpg'),
        ('Long Island City High-Rise', 'New development with amenities and skyline views', 'Queens', 'Long Island City', 
         'Condo', 1200000, 1, 1.0, 800, 'growth', 4.9, 'low', '/static/images/property8.jpg'),
        ('Forest Hills Tudor', 'Classic Tudor in prestigious neighborhood', 'Queens', 'Forest Hills', 
         'Single-family', 1350000, 3, 2.5, 2100, 'value', 3.7, 'low', '/static/images/property9.jpg'),
        
        # Bronx properties
        ('Riverdale Luxury Home', 'Spacious home with yard in upscale neighborhood', 'Bronx', 'Riverdale', 
         'Single-family', 1250000, 4, 3.0, 2800, 'luxury', 3.4, 'low', '/static/images/property10.jpg'),
        ('Mott Haven Development', 'Emerging area with strong appreciation potential', 'Bronx', 'Mott Haven', 
         'Condo', 650000, 2, 2.0, 1100, 'growth', 5.8, 'high', '/static/images/property11.jpg'),
        
        # Staten Island properties
        ('St. George Townhouse', 'Recently renovated with ferry access to Manhattan', 'Staten Island', 'St. George', 
         'Townhouse', 850000, 3, 2.5, 2200, 'cashflow', 5.3, 'medium', '/static/images/property12.jpg'),
        ('Todt Hill Estate', 'Luxury estate with large lot and privacy', 'Staten Island', 'Todt Hill', 
         'Single-family', 1650000, 5, 4.0, 4200, 'luxury', 2.9, 'low', '/static/images/property13.jpg'),
    ]
    
    cursor.executemany('''
        INSERT INTO sample_properties 
        (property_name, description, borough, neighborhood, property_type, price, 
        bedrooms, bathrooms, square_feet, investment_strategy, roi_potential, risk_level, image_url) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_properties)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {DB_PATH}")
    print(f"Added {len(sample_properties)} sample properties")

if __name__ == "__main__":
    init_db() 