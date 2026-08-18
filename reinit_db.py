#!/usr/bin/env python3
"""
Script to reinitialize the database with sample products.
"""
import os
import sys
import json
import sqlite3

# Set up correct path to workspace
sys.path.insert(0, '/Users/spidey./Downloads/Daily-Drop')

from config import Config

def main():
    print("Reinitializing product database...")
    
    # Connect to database
    db_path = Config.DATABASE_PATH
    print(f"Database path: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop products table if it exists to ensure a clean rebuild with the new schema
    cursor.execute("DROP TABLE IF EXISTS products")
    
    # Create products table with subcategory and stock columns
    cursor.execute('''
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            image_path TEXT NOT NULL,
            description TEXT,
            stock INTEGER DEFAULT 50
        )
    ''')
    conn.commit()
    
    # Load cleaned products list
    cleaned_json_path = '/Users/spidey./.gemini/antigravity-ide/brain/1fb32aa5-722f-4bb3-ac94-09024b7055b1/scratch/cleaned_products.json'
    if not os.path.exists(cleaned_json_path):
        print(f"Error: Cleaned products JSON not found at {cleaned_json_path}")
        sys.exit(1)
        
    with open(cleaned_json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
        
    print(f"Loaded {len(products)} cleaned products from JSON.")
    
    # Prepare records for insertion
    records = []
    for p in products:
        pid = p.get('id')
        unique_stock = (pid * 17 + 11) % 95
        records.append((
            pid,
            p['title'],
            p['price'],
            p['category'],
            p.get('subcategory', ''),
            p['image'],
            p.get('description', ''),
            unique_stock
        ))
        
    try:
        cursor.executemany('''
            INSERT INTO products (product_id, name, price, category, subcategory, image_path, description, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', records)
        conn.commit()
        print("✓ Database reinitialized successfully!")
        print(f"✓ Inserted {len(records)} products into the database.")
    except Exception as e:
        print(f"✗ Error inserting products: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
