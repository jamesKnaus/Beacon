-- Drop tables if they exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS investment_profiles;
DROP TABLE IF EXISTS sample_properties;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    newsletter_subscribed BOOLEAN DEFAULT 1
);

-- Create investment profiles table
CREATE TABLE investment_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    investment_strategy TEXT NOT NULL, -- value, growth, cashflow, etc.
    boroughs TEXT NOT NULL, -- Comma-separated list of NYC boroughs
    neighborhoods TEXT, -- Comma-separated list of neighborhoods
    property_types TEXT NOT NULL, -- Comma-separated list: condo, co-op, townhouse, etc.
    min_budget INTEGER,
    max_budget INTEGER,
    risk_tolerance TEXT, -- low, medium, high
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create sample properties table
CREATE TABLE sample_properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_name TEXT NOT NULL,
    description TEXT NOT NULL,
    borough TEXT NOT NULL,
    neighborhood TEXT NOT NULL,
    property_type TEXT NOT NULL,
    price INTEGER NOT NULL,
    bedrooms INTEGER,
    bathrooms REAL,
    square_feet INTEGER,
    investment_strategy TEXT NOT NULL,
    roi_potential REAL,
    risk_level TEXT,
    image_url TEXT
);
