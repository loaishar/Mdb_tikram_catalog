from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Apply all Arabic translation updates to MongoDB tikram_catalog.products collection
using the existing connection string and processing all 19 batch files
"""

import json
import os
from pymongo import MongoClient

# MongoDB connection
connection_string = "mongodb+srv://luaysharqiya_db_user:1yfBzVW8czpXussR@clustertikramcatalog.kwkrm7n.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTikramCatalog"

def apply_arabic_batch_updates(batch_number):
    """Apply Arabic updates from a specific batch file"""
    batch_file = f"arabic_update_batch_{batch_number}.json"
    
    if not os.path.exists(resolve_data(batch_file)):
        print(f"❌ Batch file {batch_file} not found")
        return 0, 0
    
    try:
        with open_data(batch_file, 'r', encoding='utf-8') as f:
            updates = json.load(f)
        
        client = MongoClient(connection_string)
        db = client.tikram_catalog
        collection = db.products
        
        updates_applied = 0
        matched_count = 0
        
        print(f"  Processing {len(updates)} updates...")
        
        for i, update_doc in enumerate(updates, 1):
            filter_criteria = update_doc['filter']
            update_operation = update_doc['update']
            
            result = collection.update_many(filter_criteria, update_operation)
            updates_applied += result.modified_count
            matched_count += result.matched_count
            
            shufersal_id = filter_criteria.get('metadata.shufersal_id', 'unknown')
            
            if result.matched_count > 0:
                if result.modified_count > 0:
                    print(f"    ✅ {i:2d}/50: Product {shufersal_id} - Updated")
                else:
                    print(f"    ℹ️  {i:2d}/50: Product {shufersal_id} - Already had Arabic translation")
            else:
                print(f"    ❌ {i:2d}/50: Product {shufersal_id} - Not found")
        
        client.close()
        print(f"    📊 Batch summary: {matched_count} matched, {updates_applied} modified")
        return matched_count, updates_applied
        
    except Exception as e:
        print(f"❌ Error processing batch {batch_number}: {e}")
        return 0, 0

def main():
    """Apply all Arabic translation batches"""
    print("🚀 Starting Arabic translation batch processing...")
    print("=" * 60)
    
    total_updates = 0
    total_matched = 0
    successful_batches = 0
    
    for batch_num in range(1, 20):  # batches 1-19
        print(f"\n📦 Processing Arabic Batch {batch_num}...")
        matched, modified = apply_arabic_batch_updates(batch_num)
        
        if matched > 0:
            successful_batches += 1
            total_matched += matched
            total_updates += modified
    
    print(f"\n" + "=" * 60)
    print(f"🎯 FINAL SUMMARY")
    print(f"=" * 60)
    print(f"Successful batches: {successful_batches}/19")
    print(f"Total products matched: {total_matched}")
    print(f"Total products updated with Arabic translations: {total_updates}")
    print(f"Expected total products: ~928")
    
    if total_matched >= 900:
        print("✅ SUCCESS: Most products found and processed!")
    elif total_matched >= 700:
        print("⚠️  WARNING: Some products may be missing from the database")
    else:
        print("❌ ERROR: Many products not found - check database connection")

if __name__ == "__main__":
    main()
