#!/usr/bin/env python3
"""
Prepare offers for MCP MongoDB import
"""

import json

def load_offers_for_import():
    """Load the converted offers and prepare them for MCP import"""
    
    with open('mongodb_import_batch_1.json', 'r', encoding='utf-8') as f:
        offers = json.load(f)
    
    print(f"Loaded {len(offers)} offers for import")
    print("\nFirst offer:")
    print(json.dumps(offers[0], indent=2, ensure_ascii=False))
    
    # Save first 10 offers for initial testing
    test_batch = offers[:10]
    with open('test_import_offers.json', 'w', encoding='utf-8') as f:
        json.dump(test_batch, f, ensure_ascii=False, indent=2)
    print(f"\nSaved first 10 offers to test_import_offers.json for testing")
    
    return offers

if __name__ == "__main__":
    offers = load_offers_for_import()