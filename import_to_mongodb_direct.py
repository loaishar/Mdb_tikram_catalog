#!/usr/bin/env python3
"""
Direct import to MongoDB - preparing data for MCP import
"""
import json

def prepare_batch_for_mcp(batch_num):
    """Prepare a batch for MCP MongoDB import"""
    with open(f'mongo_batch_{batch_num}.json', 'r', encoding='utf-8') as f:
        batch = json.load(f)
    
    # Return the batch data
    return batch

def get_all_batches():
    """Get all batch numbers"""
    with open('import_status.json', 'r', encoding='utf-8') as f:
        status = json.load(f)
    return status['batch_count']

if __name__ == "__main__":
    total_batches = get_all_batches()
    print(f"Total batches to import: {total_batches}")
    
    # Prepare first batch
    batch_1 = prepare_batch_for_mcp(1)
    print(f"Batch 1 ready: {len(batch_1)} products")
    print(f"First product: {batch_1[0]['name']}")
    print(f"Last product: {batch_1[-1]['name']}")