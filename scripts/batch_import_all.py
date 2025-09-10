from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Import all 928 products to MongoDB in batches
"""
import json
import os

def load_all_products():
    """Load all products from the prepared file"""
    with open_data('all_products_import.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def split_into_batches(products, batch_size=50):
    """Split products into manageable batches"""
    batches = []
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        batches.append(batch)
    return batches

def save_batch_for_import(batch, batch_num):
    """Save a batch for MongoDB import"""
    filename = f'mongo_batch_{batch_num}.json'
    with open_data(filename, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False)
    return filename

def main():
    """Main import orchestration"""
    print("Loading all products...")
    products = load_all_products()
    print(f"Loaded {len(products)} products")
    
    # Split into batches of 50
    batches = split_into_batches(products, batch_size=50)
    print(f"Split into {len(batches)} batches")
    
    # Track imported products
    imported_count = 0
    batch_files = []
    
    # Save each batch
    for i, batch in enumerate(batches):
        filename = save_batch_for_import(batch, i+1)
        batch_files.append(filename)
        imported_count += len(batch)
        print(f"Batch {i+1}: {len(batch)} products saved to {filename}")
    
    print(f"\n=== Import Summary ===")
    print(f"Total products: {len(products)}")
    print(f"Total batches: {len(batches)}")
    print(f"Batch size: 50 products")
    print(f"Files created: {len(batch_files)}")
    
    # Create import status file
    status = {
        "total_products": len(products),
        "batch_count": len(batches),
        "batch_files": batch_files,
        "status": "ready_for_import"
    }
    
    with open_data('import_status.json', 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    print("\nImport status saved to import_status.json")
    print("Ready to import to MongoDB!")

if __name__ == "__main__":
    main()
