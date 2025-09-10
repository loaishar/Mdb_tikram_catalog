#!/usr/bin/env python3
"""
Apply all translation updates to MongoDB
"""
import json
import glob

def apply_updates():
    """Read and apply all update batches"""
    
    # Get all update batch files
    batch_files = sorted(glob.glob('update_batch_*.json'))
    print(f"Found {len(batch_files)} batch files to process")
    
    total_updates = 0
    
    for batch_file in batch_files:
        with open(batch_file, 'r', encoding='utf-8') as f:
            updates = json.load(f)
        
        print(f"\nProcessing {batch_file} with {len(updates)} updates...")
        
        # Print MCP commands for each batch
        for i, update in enumerate(updates):
            if i == 0:  # Just show first update as example
                print(f"Sample update: {json.dumps(update, ensure_ascii=False)[:200]}...")
        
        total_updates += len(updates)
    
    print(f"\n=== Summary ===")
    print(f"Total updates to apply: {total_updates}")
    print(f"All updates add:")
    print("  - name_en: English translation of product name")
    print("  - aliases.en: Array with English name")
    print("  - aliases.ar: Empty array for Arabic (ready for future translations)")
    print("  - brand_en: English brand name (where applicable)")
    
    return batch_files

if __name__ == "__main__":
    print("Analyzing translation updates...")
    batch_files = apply_updates()