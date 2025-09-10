#!/usr/bin/env python3
"""
Batch import products and offers into MongoDB with deduplication
"""
import json
from datetime import datetime

# MongoDB IDs
TIKRAM_SHOP_MERCHANT_ID = "68bf06365371c586220eb9f7"
DAIRY_EGGS_CATEGORY_ID = "68bef17f5371c586220eb9ea"

def load_json_files():
    """Load the generated JSON files"""
    with open('products_import.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    with open('offers_import.json', 'r', encoding='utf-8') as f:
        offers = json.load(f)
    
    return products, offers

def prepare_batch_import():
    """Prepare data for batch import with deduplication logic"""
    products, offers = load_json_files()
    
    print(f"Loaded {len(products)} products and {len(offers)} offers")
    
    # Group products by brand for easier processing
    products_by_brand = {}
    for product in products:
        brand = product.get('brand', 'Unknown')
        if brand not in products_by_brand:
            products_by_brand[brand] = []
        products_by_brand[brand].append(product)
    
    print("\n=== Products by Brand ===")
    for brand, brand_products in sorted(products_by_brand.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"{brand}: {len(brand_products)} products")
    
    # Prepare batches for import (50 products per batch for safety)
    batch_size = 50
    product_batches = []
    
    all_products_flat = []
    for brand in products_by_brand:
        all_products_flat.extend(products_by_brand[brand])
    
    for i in range(0, len(all_products_flat), batch_size):
        batch = all_products_flat[i:i+batch_size]
        product_batches.append(batch)
    
    print(f"\nCreated {len(product_batches)} batches of products (batch size: {batch_size})")
    
    # Save batches for import
    with open('products_batch_1.json', 'w', encoding='utf-8') as f:
        json.dump(product_batches[0] if product_batches else [], f, ensure_ascii=False, indent=2)
    
    print("\nFirst batch saved to products_batch_1.json")
    print("Ready for import!")
    
    return product_batches, offers

def generate_import_commands():
    """Generate MongoDB import commands"""
    product_batches, offers = prepare_batch_import()
    
    print("\n=== Import Instructions ===")
    print(f"Total batches to import: {len(product_batches)}")
    print(f"Total offers to import: {len(offers)}")
    
    # Save all batches
    for i, batch in enumerate(product_batches):
        filename = f'products_batch_{i+1}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
        print(f"Saved batch {i+1} to {filename} ({len(batch)} products)")
    
    print("\n✅ All batches prepared for import")
    print("\nNext steps:")
    print("1. Import products batch by batch using MCP MongoDB tools")
    print("2. Map product IDs from import results")
    print("3. Import offers with correct product IDs")

if __name__ == "__main__":
    generate_import_commands()