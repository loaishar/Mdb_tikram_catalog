from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Import offers for Tikram catalog
This script:
1. Gets mapping of shufersal_id to MongoDB _id from products collection
2. Processes all offers batch files (offers_batch_1.json through offers_batch_10.json)
3. Replaces shufersal_id with product_id from MongoDB
4. Imports offers using MCP MongoDB tools
"""

import json
import os
from collections import defaultdict

def load_json_file(filename):
    """Load JSON file"""
    try:
        with open_data(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {filename}: {e}")
        return []

def process_offers():
    """Process all offer batch files"""
    
    # This mapping will be populated from MongoDB query results
    # Format: {"P_42015": "68bf0a207596a1f78d625214", ...}
    product_mapping = {}
    
    # We'll need to get this mapping from MongoDB first
    print("Need to get product mapping from MongoDB products collection first...")
    print("Run the MCP MongoDB find query to get all products with shufersal_id and _id")
    
    # Process each batch file
    total_offers = 0
    batch_counts = []
    
    for batch_num in range(1, 11):
        filename = f"offers_batch_{batch_num}.json"
        
        if not os.path.exists(resolve_data(filename)):
            print(f"Batch file {filename} not found, skipping...")
            continue
            
        print(f"Processing {filename}...")
        offers_data = load_json_file(filename)
        
        if not offers_data:
            print(f"No data in {filename}")
            continue
            
        # Process offers in this batch
        processed_offers = []
        missing_products = set()
        
        for offer in offers_data:
            shufersal_id = offer.get('shufersal_id')
            
            if not shufersal_id:
                print(f"Offer missing shufersal_id: {offer}")
                continue
                
            # Replace shufersal_id with product_id from mapping
            if shufersal_id in product_mapping:
                # Create new offer document with product_id
                processed_offer = offer.copy()
                processed_offer['product_id'] = product_mapping[shufersal_id]
                del processed_offer['shufersal_id']  # Remove shufersal_id
                processed_offers.append(processed_offer)
            else:
                missing_products.add(shufersal_id)
        
        if missing_products:
            print(f"Warning: {len(missing_products)} products not found in mapping:")
            for pid in list(missing_products)[:5]:  # Show first 5
                print(f"  {pid}")
            if len(missing_products) > 5:
                print(f"  ... and {len(missing_products) - 5} more")
        
        print(f"Batch {batch_num}: {len(processed_offers)} offers ready for import")
        batch_counts.append(len(processed_offers))
        total_offers += len(processed_offers)
        
        # Save processed batch for import
        output_filename = f"processed_offers_batch_{batch_num}.json"
        with open_data(output_filename, 'w', encoding='utf-8') as f:
            json.dump(processed_offers, f, ensure_ascii=False, indent=2)
        print(f"Saved processed offers to {output_filename}")
    
    print(f"\nSummary:")
    print(f"Total offers processed: {total_offers}")
    for i, count in enumerate(batch_counts, 1):
        print(f"Batch {i}: {count} offers")
    
    return batch_counts, total_offers

if __name__ == "__main__":
    print("=== Offers Import Script ===")
    print("This script prepares offer batches for MongoDB import")
    print("First, we need to get the product mapping from MongoDB...")
    
    # For now, just show what needs to be done
    print("\nSteps needed:")
    print("1. Get all products from MongoDB with projection: {'metadata.shufersal_id': 1, '_id': 1}")
    print("2. Build mapping dictionary")
    print("3. Process each offers batch file")
    print("4. Import processed batches to MongoDB")
    
    process_offers()
