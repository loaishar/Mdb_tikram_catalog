from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Import offers batch to MongoDB
"""

import json

def load_and_print_for_import(filename, chunk_size=10):
    """Load offers and print them in chunks for manual import"""
    
    with open_data(filename, 'r', encoding='utf-8') as f:
        offers = json.load(f)
    
    print(f"Loaded {len(offers)} offers from {filename}")
    
    # Split into chunks
    for i in range(0, len(offers), chunk_size):
        chunk = offers[i:i+chunk_size]
        print(f"\n=== Chunk {i//chunk_size + 1}: {len(chunk)} offers ===")
        print("Use this data with mcp__mongodb__insert-many:")
        print(json.dumps(chunk, ensure_ascii=False, separators=(',', ':')))
        print(f"--- End of chunk {i//chunk_size + 1} ---\n")

def main():
    print("=== Import Batch to MongoDB ===")
    load_and_print_for_import('mongodb_import_batch_1.json', chunk_size=10)

if __name__ == "__main__":
    main()
