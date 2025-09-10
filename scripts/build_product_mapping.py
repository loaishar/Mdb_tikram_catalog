from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Build product mapping from MongoDB results
This script processes the product data to create mapping files for the offers import
"""

import json

# Sample MongoDB query results - we'll collect these from multiple queries
# Format: {"_id":"68bf0a207596a1f78d625214","metadata":{"shufersal_id":"P_42015"}}

def build_mapping_from_results(results_data):
    """Build mapping dictionary from MongoDB results"""
    mapping = {}
    
    for doc in results_data:
        if 'metadata' in doc and 'shufersal_id' in doc['metadata']:
            shufersal_id = doc['metadata']['shufersal_id']
            mongo_id = doc['_id']
            mapping[shufersal_id] = mongo_id
    
    return mapping

def save_mapping(mapping, filename="product_mapping.json"):
    """Save mapping to JSON file"""
    with open_data(filename, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(mapping)} product mappings to {filename}")

if __name__ == "__main__":
    print("=== Product Mapping Builder ===")
    print("Collect MongoDB query results and build mapping file")
    
    # We'll collect the results and build the mapping
    print("Ready to process MongoDB results...")
