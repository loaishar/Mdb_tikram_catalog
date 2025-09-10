from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Complete remaining translation update batches 15-19 using the established connection
"""

import json
import subprocess
import sys

def apply_single_update(database, collection, filter_doc, update_doc):
    """Apply a single update using mcp__mongodb__update-many"""
    try:
        # Since we can't directly call MCP tools from Python, we'll output the commands needed
        print(f"UPDATE: {filter_doc} -> {update_doc}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def process_batch_file(batch_number):
    """Process a specific batch file"""
    batch_file = f"update_batch_{batch_number}.json"
    
    try:
        with open_data(batch_file, 'r', encoding='utf-8') as f:
            updates = json.load(f)
        
        print(f"\n=== BATCH {batch_number} - {len(updates)} updates ===")
        
        success_count = 0
        for i, update_doc in enumerate(updates):
            filter_criteria = update_doc['filter']
            update_operation = update_doc['update']
            
            # Extract the shufersal_id for easier tracking
            shufersal_id = filter_criteria.get('metadata.shufersal_id', 'unknown')
            
            # Format for manual execution
            print(f"#{i+1}: ID {shufersal_id}")
            print(f"  Filter: {json.dumps(filter_criteria)}")
            print(f"  Update: {json.dumps(update_operation)}")
            
            success_count += 1
        
        print(f"Batch {batch_number} prepared: {success_count} updates")
        return success_count
        
    except Exception as e:
        print(f"Error processing batch {batch_number}: {e}")
        return 0

def main():
    """Process batches 15-19"""
    print("Completing translation updates for batches 15-19")
    
    total_updates = 0
    for batch_num in range(15, 20):  # batches 15-19
        updates_count = process_batch_file(batch_num)
        total_updates += updates_count
    
    print(f"\n=== SUMMARY ===")
    print(f"Total updates prepared for batches 15-19: {total_updates}")

if __name__ == "__main__":
    main()
