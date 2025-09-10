#!/usr/bin/env python3
"""
Complete the import of batch 1 offers
"""

import json

def import_remaining_offers():
    """Import remaining offers from batch 1"""
    
    with open('mongodb_import_batch_1.json', 'r') as f:
        offers = json.load(f)
    
    # We've imported 8 offers, 42 remaining
    remaining = offers[8:]
    
    print(f"Remaining offers to import: {len(remaining)}")
    
    # Split into manageable chunks for import
    chunk_size = 20  # Larger chunks to be more efficient
    
    for i in range(0, len(remaining), chunk_size):
        chunk = remaining[i:i+chunk_size]
        chunk_num = i//chunk_size + 1
        
        print(f"\n=== Chunk {chunk_num}: {len(chunk)} offers ===")
        
        # Create a file for this chunk
        chunk_filename = f"import_chunk_{chunk_num}.json"
        with open(chunk_filename, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
        
        print(f"Saved chunk to {chunk_filename}")
        print(f"Contains offers from index {8+i} to {8+i+len(chunk)-1}")
        
        # Show command to import this chunk
        print(f"Use: mcp__mongodb__insert-many with documents from {chunk_filename}")

if __name__ == "__main__":
    import_remaining_offers()