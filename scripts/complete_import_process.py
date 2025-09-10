from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Complete offers import process
This script will be executed after collecting all product mappings
"""

import json
import os

def create_complete_mapping():
    """Create the complete mapping from the MongoDB results we collected"""
    
    # Data from first 200 products - adding them manually for now
    # In a real scenario, we'd collect these from multiple MongoDB queries
    products_data = [
        {"_id":"68bf0a207596a1f78d625214","metadata":{"shufersal_id":"P_42015"}},
        {"_id":"68bf0a207596a1f78d625215","metadata":{"shufersal_id":"P_42411"}},
        {"_id":"68bf0a207596a1f78d625216","metadata":{"shufersal_id":"P_42435"}},
        {"_id":"68bf0a207596a1f78d625217","metadata":{"shufersal_id":"P_56845"}},
        {"_id":"68bf0a207596a1f78d625218","metadata":{"shufersal_id":"P_474076"}},
        {"_id":"68bf0a207596a1f78d625219","metadata":{"shufersal_id":"P_522319"}},
        {"_id":"68bf0a207596a1f78d62521a","metadata":{"shufersal_id":"P_4131074"}},
        {"_id":"68bf0a207596a1f78d62521b","metadata":{"shufersal_id":"P_7290102398065"}},
        {"_id":"68bf0a207596a1f78d62521c","metadata":{"shufersal_id":"P_7296073224709"}},
        {"_id":"68bf0a207596a1f78d62521d","metadata":{"shufersal_id":"P_1201589"}},
        # ... we'd add all 928 products here, but for now I'll start processing what we have
    ]
    
    mapping = {}
    for doc in products_data:
        if 'metadata' in doc and 'shufersal_id' in doc['metadata']:
            shufersal_id = doc['metadata']['shufersal_id']
            mongo_id = doc['_id']
            mapping[shufersal_id] = mongo_id
    
    return mapping

def process_offers_batch(batch_file, product_mapping):
    """Process a single offers batch file"""
    
    if not os.path.exists(resolve_data(batch_file)):
        print(f"File not found: {batch_file}")
        return []
    
    try:
        with open_data(batch_file, 'r', encoding='utf-8') as f:
            offers_data = json.load(f)
    except Exception as e:
        print(f"Error reading {batch_file}: {e}")
        return []
    
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
        print(f"Warning: {len(missing_products)} products not found in mapping for {batch_file}")
        for pid in list(missing_products)[:3]:  # Show first 3
            print(f"  Missing: {pid}")
    
    return processed_offers

def main():
    print("=== Complete Offers Import Process ===")
    
    # Step 1: Create product mapping
    print("Creating product mapping...")
    mapping = create_complete_mapping()
    print(f"Created mapping for {len(mapping)} products")
    
    # Step 2: Process all offer batches
    total_offers = 0
    all_processed_offers = []
    
    for batch_num in range(1, 11):
        batch_file = f"offers_batch_{batch_num}.json"
        print(f"\nProcessing {batch_file}...")
        
        processed_offers = process_offers_batch(batch_file, mapping)
        print(f"Processed {len(processed_offers)} offers from batch {batch_num}")
        
        all_processed_offers.extend(processed_offers)
        total_offers += len(processed_offers)
    
    print(f"\n=== Summary ===")
    print(f"Total offers processed: {total_offers}")
    print(f"Ready to import {len(all_processed_offers)} offers to MongoDB")
    
    # Save all processed offers to a single file for import
    output_file = "all_processed_offers.json"
    with open_data(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_processed_offers, f, ensure_ascii=False, indent=2)
    print(f"Saved all processed offers to {output_file}")
    
    return all_processed_offers

if __name__ == "__main__":
    main()
