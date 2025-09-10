from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Import first batch to MongoDB and create product-offer mapping
"""
import json

def load_batch_1():
    """Load first batch of products"""
    with open_data('products_batch_1.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # Clean up the products for MongoDB import
    cleaned_products = []
    for product in products:
        # Remove the $oid wrapper for category_id
        if 'category_id' in product and '$oid' in product['category_id']:
            product['category_id'] = product['category_id']['$oid']
        
        # Remove the $date wrapper for imported_at
        if 'metadata' in product and 'imported_at' in product['metadata']:
            if '$date' in product['metadata']['imported_at']:
                product['metadata']['imported_at'] = product['metadata']['imported_at']['$date']
        
        cleaned_products.append(product)
    
    return cleaned_products

def create_import_ready_batch():
    """Create import-ready documents"""
    products = load_batch_1()
    
    # Save cleaned batch
    with open_data('batch_1_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"Prepared {len(products)} products for import")
    print("Saved to batch_1_cleaned.json")
    
    # Show first product as example
    print("\nFirst product example:")
    print(json.dumps(products[0], ensure_ascii=False, indent=2))
    
    return products

if __name__ == "__main__":
    create_import_ready_batch()
