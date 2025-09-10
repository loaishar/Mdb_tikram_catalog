#!/usr/bin/env python3
import json
import sys

def load_batch_file(batch_num):
    """Load a batch file and return the documents"""
    filename = f"/home/loai1/projects/Mdb_tikram_catalog/mongo_batch_{batch_num}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Batch file {filename} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in batch {batch_num}: {e}")
        return None

def main():
    """Load all batches and print summary"""
    total_products = 0
    batch_summary = []
    
    for i in range(1, 20):  # Batches 1-19
        docs = load_batch_file(i)
        if docs is not None:
            count = len(docs)
            batch_summary.append(f"Batch {i}: {count} products")
            total_products += count
            print(f"Batch {i}: {count} products")
        else:
            batch_summary.append(f"Batch {i}: FAILED")
            print(f"Batch {i}: FAILED to load")
    
    print(f"\nTotal products across all batches: {total_products}")
    print(f"Expected total: 928")
    print(f"Match: {'YES' if total_products == 928 else 'NO'}")

if __name__ == "__main__":
    main()