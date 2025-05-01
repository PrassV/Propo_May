#!/usr/bin/env python
"""
This script creates the necessary tables in Supabase.
Run this script once to set up your Supabase database.
"""

import httpx
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    sys.exit(1)

async def execute_sql(sql):
    """Execute SQL against Supabase PostgreSQL database."""
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # SQL query endpoint
    endpoint = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql"
    
    # Make the request
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint, 
                headers=headers,
                json={"query": sql}
            )
            
            if response.status_code >= 400:
                print(f"Error {response.status_code}: {response.text}")
                return False
                
            print(f"SQL executed successfully: {sql[:50]}...")
            return True
    
    except Exception as e:
        print(f"Error executing SQL: {str(e)}")
        return False

async def create_tables():
    """Create all required tables in the Supabase database."""
    
    # Users table
    users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR NOT NULL UNIQUE,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR NOT NULL,
        phone VARCHAR,
        role VARCHAR NOT NULL,
        profile_picture_url VARCHAR,
        email_verified BOOLEAN DEFAULT FALSE,
        status VARCHAR DEFAULT 'active',
        last_login_at TIMESTAMP,
        supabase_uid VARCHAR UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Enable RLS on users table
    ALTER TABLE users ENABLE ROW LEVEL SECURITY;

    -- Create RLS policies for users table
    CREATE POLICY "Users can view their own data" ON users
        FOR SELECT USING (auth.uid()::text = supabase_uid);
        
    CREATE POLICY "Users can update their own data" ON users
        FOR UPDATE USING (auth.uid()::text = supabase_uid);
        
    CREATE POLICY "Admins can view all users" ON users
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.supabase_uid = auth.uid()::text 
                AND users.role = 'admin'
            )
        );
        
    CREATE POLICY "Admins can update all users" ON users
        FOR UPDATE USING (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.supabase_uid = auth.uid()::text 
                AND users.role = 'admin'
            )
        );
    """
    
    # Properties table
    properties_table_sql = """
    CREATE TABLE IF NOT EXISTS properties (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR NOT NULL,
        street VARCHAR NOT NULL,
        city VARCHAR NOT NULL,
        state VARCHAR NOT NULL,
        zip VARCHAR NOT NULL,
        country VARCHAR DEFAULT 'USA',
        latitude NUMERIC(10, 8),
        longitude NUMERIC(11, 8),
        property_type VARCHAR NOT NULL,
        year_built INTEGER,
        total_units INTEGER NOT NULL,
        amenities TEXT[],
        description TEXT,
        status VARCHAR DEFAULT 'active',
        tax_id VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Enable RLS on properties table
    ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

    -- Create RLS policies for properties table
    CREATE POLICY "Owners can view their own properties" ON properties
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.id = owner_id 
                AND users.supabase_uid = auth.uid()::text
            )
        );
        
    CREATE POLICY "Owners can update their own properties" ON properties
        FOR UPDATE USING (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.id = owner_id 
                AND users.supabase_uid = auth.uid()::text
            )
        );
        
    CREATE POLICY "Owners can create properties" ON properties
        FOR INSERT WITH CHECK (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.id = owner_id 
                AND users.supabase_uid = auth.uid()::text
            )
        );
        
    CREATE POLICY "Admins can view all properties" ON properties
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.supabase_uid = auth.uid()::text 
                AND users.role = 'admin'
            )
        );
    """
    
    # Units table
    units_table_sql = """
    CREATE TABLE IF NOT EXISTS units (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
        unit_number VARCHAR NOT NULL,
        floor INTEGER,
        bedrooms NUMERIC(3, 1) NOT NULL,
        bathrooms NUMERIC(3, 1) NOT NULL,
        square_feet INTEGER NOT NULL,
        rent_amount NUMERIC(10, 2) NOT NULL,
        security_deposit NUMERIC(10, 2) NOT NULL,
        status VARCHAR DEFAULT 'available',
        amenities TEXT[],
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Enable RLS on units table
    ALTER TABLE units ENABLE ROW LEVEL SECURITY;

    -- Create RLS policies for units table
    CREATE POLICY "Owners can view units in their properties" ON units
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM properties 
                JOIN users ON properties.owner_id = users.id
                WHERE properties.id = property_id 
                AND users.supabase_uid = auth.uid()::text
            )
        );
        
    CREATE POLICY "Owners can update units in their properties" ON units
        FOR UPDATE USING (
            EXISTS (
                SELECT 1 FROM properties 
                JOIN users ON properties.owner_id = users.id
                WHERE properties.id = property_id 
                AND users.supabase_uid = auth.uid()::text
            )
        );
        
    CREATE POLICY "Owners can create units in their properties" ON units
        FOR INSERT WITH CHECK (
            EXISTS (
                SELECT 1 FROM properties 
                JOIN users ON properties.owner_id = users.id
                WHERE properties.id = property_id 
                AND users.supabase_uid = auth.uid()::text
            )
        );
        
    CREATE POLICY "Admins can view all units" ON units
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM users 
                WHERE users.supabase_uid = auth.uid()::text 
                AND users.role = 'admin'
            )
        );
    """
    
    # Execute SQL for each table
    success = await execute_sql(users_table_sql)
    if success:
        success = await execute_sql(properties_table_sql)
    if success:
        success = await execute_sql(units_table_sql)
        
    return success

if __name__ == "__main__":
    import asyncio
    
    print("Creating tables in Supabase...")
    success = asyncio.run(create_tables())
    
    if success:
        print("All tables created successfully!")
    else:
        print("Error creating tables. Check the output above for details.") 