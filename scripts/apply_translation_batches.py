from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Apply all translation update batches to MongoDB tikram_catalog.products collection
"""

import json
import os
from pymongo import MongoClient

# MongoDB connection
connection_string = "mongodb+srv://luaysharqiya_db_user:1yfBzVW8czpXussR@clustertikramcatalog.kwkrm7n.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTikramCatalog"

def apply_batch_updates(batch_number):
    """Apply updates from a specific batch file"""
    batch_file = f"update_batch_{batch_number}.json"
    
    if not os.path.exists(resolve_data(batch_file)):
        print(f"Batch file {batch_file} not found")
        return 0
    
    try:
        with open_data(batch_file, 'r', encoding='utf-8') as f:
            updates = json.load(f)
        
        client = MongoClient(connection_string)
        db = client.tikram_catalog
        collection = db.products
        
        updates_applied = 0
        for update_doc in updates:
            filter_criteria = update_doc['filter']
            update_operation = update_doc['update']
            
            result = collection.update_many(filter_criteria, update_operation)
            updates_applied += result.modified_count
            
            if result.matched_count > 0:
                print(f"  Updated product {filter_criteria.get('metadata.shufersal_id', 'unknown')} - Modified: {result.modified_count}")
        
        print(f"Batch {batch_number}: Applied {updates_applied} updates from {len(updates)} operations")
        client.close()
        return updates_applied
        
    except Exception as e:
        print(f"Error processing batch {batch_number}: {e}")
        return 0

def main():
    """Apply all translation batches"""
    total_updates = 0
    
    for batch_num in range(1, 20):  # batches 1-19
        print(f"\nProcessing batch {batch_num}...")
        updates_count = apply_batch_updates(batch_num)
        total_updates += updates_count
    
    print(f"\n=== SUMMARY ===")
    print(f"Total updates applied across all batches: {total_updates}")

if __name__ == "__main__":
    main()
