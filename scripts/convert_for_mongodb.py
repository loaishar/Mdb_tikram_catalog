from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Convert processed offers to MongoDB-compatible format
"""

import json
from datetime import datetime

def convert_mongodb_extended_json(obj):
    """Convert MongoDB extended JSON format to Python objects"""
    if isinstance(obj, dict):
        if "$oid" in obj:
            return obj["$oid"]  # Convert ObjectId to string
        elif "$date" in obj:
            return obj["$date"]  # Keep date as string for now
        else:
            return {k: convert_mongodb_extended_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_mongodb_extended_json(item) for item in obj]
    else:
        return obj

def convert_offers_file(input_file, output_file):
    """Convert a processed offers file to MongoDB-compatible format"""
    
    try:
        with open_data(input_file, 'r', encoding='utf-8') as f:
            offers = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return 0
    
    # Convert each offer
    converted_offers = []
    for offer in offers:
        converted_offer = convert_mongodb_extended_json(offer)
        converted_offers.append(converted_offer)
    
    # Save converted offers
    with open_data(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_offers, f, ensure_ascii=False, indent=2)
    
    print(f"Converted {len(converted_offers)} offers from {input_file} to {output_file}")
    return len(converted_offers)

def main():
    print("=== Converting Offers for MongoDB Import ===")
    
    # Convert batch 1
    count = convert_offers_file('ready_for_import_batch_1.json', 'mongodb_import_batch_1.json')
    print(f"Ready to import {count} offers from batch 1")

if __name__ == "__main__":
    main()
