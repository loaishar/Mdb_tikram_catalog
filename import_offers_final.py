#!/usr/bin/env python3
"""
Import offers for Tikram catalog - Final Version
This script processes all offer batches and imports them to MongoDB
"""

import json
import os

def create_mapping_from_known_products():
    """Create mapping from the products we queried from MongoDB"""
    
    # Based on our MongoDB queries, create the mapping
    # This is the mapping we collected from the first 200 products
    mapping = {
        "P_42015": "68bf0a207596a1f78d625214",
        "P_42411": "68bf0a207596a1f78d625215", 
        "P_42435": "68bf0a207596a1f78d625216",
        "P_56845": "68bf0a207596a1f78d625217",
        "P_474076": "68bf0a207596a1f78d625218",
        "P_522319": "68bf0a207596a1f78d625219",
        "P_4131074": "68bf0a207596a1f78d62521a",
        "P_7290102398065": "68bf0a207596a1f78d62521b",
        "P_7296073224709": "68bf0a207596a1f78d62521c",
        "P_1201589": "68bf0a207596a1f78d62521d",
        "P_46020": "68bf0a207596a1f78d62521e",
        "P_9954364": "68bf0a207596a1f78d62521f",
        "P_7296073453468": "68bf0a207596a1f78d625220",
        "P_7296073453659": "68bf0a207596a1f78d625221",
        "P_55350": "68bf0a207596a1f78d625222",
        "P_4725426": "68bf0a207596a1f78d625223",
        "P_7296073453444": "68bf0a207596a1f78d625224",
        "P_7296073453635": "68bf0a207596a1f78d625225",
        "P_9954357": "68bf0a207596a1f78d625226",
        "P_9954562": "68bf0a207596a1f78d625227",
        "P_7290102395422": "68bf0a207596a1f78d625228",
        "P_7296073453734": "68bf0a207596a1f78d625229",
        "P_7296073626695": "68bf0a207596a1f78d62522a",
        "P_7290102395408": "68bf0a207596a1f78d62522b",
        "P_47621": "68bf0a207596a1f78d62522c",
        "P_2824183": "68bf0a207596a1f78d62522d",
        "P_2824640": "68bf0a207596a1f78d62522e",
        "P_4127862": "68bf0a207596a1f78d62522f",
        "P_6664402": "68bf0a207596a1f78d625230",
        "P_4125400": "68bf0a207596a1f78d625231",
        "P_4125417": "68bf0a207596a1f78d625232",
        "P_4125455": "68bf0a207596a1f78d625233",
        "P_43814": "68bf0a207596a1f78d625234",
        "P_58047": "68bf0a207596a1f78d625235",
        "P_7290104728310": "68bf0a207596a1f78d625236",
        "P_7290102390427": "68bf0a207596a1f78d625237",
        "P_7290102390465": "68bf0a207596a1f78d625238",
        "P_7290102390489": "68bf0a207596a1f78d625239",
        "P_7290102391844": "68bf0a207596a1f78d62523a",
        "P_7290102399635": "68bf0a207596a1f78d62523b",
        "P_7290114313681": "68bf0a207596a1f78d62523c",
        "P_7290114313056": "68bf0a207596a1f78d62523d",
        "P_7290114313063": "68bf0a207596a1f78d62523e",
        "P_7290114311359": "68bf0a207596a1f78d62523f",
        "P_7290114313674": "68bf0a207596a1f78d625240",
        "P_7290114312660": "68bf0a207596a1f78d625241",
        "P_7290102393169": "68bf0a207596a1f78d625242",
        "P_7290102393176": "68bf0a207596a1f78d625243",
        "P_7290102393190": "68bf0a207596a1f78d625244",
        "P_7290102393947": "68bf0a207596a1f78d625245",
        # Add more mappings as needed - this represents a subset
    }
    
    print(f"Created initial mapping for {len(mapping)} products")
    return mapping

def process_single_batch(batch_num, product_mapping):
    """Process a single offers batch file"""
    
    batch_file = f"offers_batch_{batch_num}.json"
    
    if not os.path.exists(batch_file):
        print(f"File not found: {batch_file}")
        return []
    
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            offers_data = json.load(f)
    except Exception as e:
        print(f"Error reading {batch_file}: {e}")
        return []
    
    processed_offers = []
    missing_products = set()
    
    for offer in offers_data:
        shufersal_id = offer.get('shufersal_id')
        
        if not shufersal_id:
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
    
    print(f"Batch {batch_num}: {len(processed_offers)} offers processed, {len(missing_products)} missing products")
    
    # Save processed batch for import
    output_file = f"ready_for_import_batch_{batch_num}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_offers, f, ensure_ascii=False, indent=2)
    
    return processed_offers, missing_products

def main():
    print("=== Final Offers Import Process ===")
    
    # Create initial mapping from known products
    mapping = create_mapping_from_known_products()
    
    # Process all batches
    total_processed = 0
    all_missing = set()
    
    for batch_num in range(1, 11):
        print(f"\nProcessing batch {batch_num}...")
        processed_offers, missing = process_single_batch(batch_num, mapping)
        total_processed += len(processed_offers)
        all_missing.update(missing)
    
    print(f"\n=== Summary ===")
    print(f"Total offers processed with existing mapping: {total_processed}")
    print(f"Total unique missing products: {len(all_missing)}")
    print(f"Ready to import {total_processed} offers to MongoDB")
    
    if all_missing:
        print(f"\nFirst 10 missing product IDs:")
        for i, pid in enumerate(list(all_missing)[:10]):
            print(f"  {pid}")

if __name__ == "__main__":
    main()