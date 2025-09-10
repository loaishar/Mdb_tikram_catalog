#!/usr/bin/env python3
import json
import sys
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

def convert_extended_json(obj):
    """Convert MongoDB extended JSON format to Python objects"""
    if isinstance(obj, dict):
        if '$oid' in obj:
            return ObjectId(obj['$oid'])
        elif '$date' in obj:
            # Parse ISO datetime string
            date_str = obj['$date']
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        else:
            return {k: convert_extended_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_extended_json(item) for item in obj]
    else:
        return obj

def import_batch(batch_num, collection):
    """Import a specific batch file to MongoDB"""
    filename = f"/home/loai1/projects/Mdb_tikram_catalog/mongo_batch_{batch_num}.json"
    
    try:
        # Load the batch file
        with open(filename, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Convert extended JSON format
        converted_data = convert_extended_json(raw_data)
        
        # Insert into MongoDB
        result = collection.insert_many(converted_data)
        
        return {
            'batch': batch_num,
            'success': True,
            'inserted_count': len(result.inserted_ids),
            'error': None
        }
        
    except Exception as e:
        return {
            'batch': batch_num, 
            'success': False,
            'inserted_count': 0,
            'error': str(e)
        }

def main():
    # MongoDB connection
    connection_string = "mongodb+srv://luaysharqiya_db_user:1yfBzVW8czpXussR@clustertikramcatalog.kwkrm7n.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTikramCatalog"
    
    try:
        client = MongoClient(connection_string)
        db = client['tikram_catalog']
        collection = db['products']
        
        # Clear existing products
        print("Clearing existing products...")
        delete_result = collection.delete_many({})
        print(f"Deleted {delete_result.deleted_count} existing products")
        
        # Import all batches
        results = []
        total_imported = 0
        
        print("\\nStarting batch imports...")
        for batch_num in range(1, 20):  # Batches 1-19
            print(f"Importing batch {batch_num}...", end=' ')
            result = import_batch(batch_num, collection)
            results.append(result)
            
            if result['success']:
                total_imported += result['inserted_count']
                print(f"✓ {result['inserted_count']} products")
            else:
                print(f"✗ Error: {result['error']}")
        
        # Summary
        print(f"\\n=== IMPORT SUMMARY ===")
        successful_batches = sum(1 for r in results if r['success'])
        failed_batches = len(results) - successful_batches
        
        print(f"Successful batches: {successful_batches}/19")
        print(f"Failed batches: {failed_batches}")
        print(f"Total products imported: {total_imported}")
        print(f"Expected total: 928")
        print(f"Import complete: {'✓' if total_imported == 928 else '✗'}")
        
        # Verify final count
        final_count = collection.count_documents({})
        print(f"\\nFinal verification - Products in database: {final_count}")
        
        if failed_batches > 0:
            print("\\nFailed batches:")
            for result in results:
                if not result['success']:
                    print(f"  Batch {result['batch']}: {result['error']}")
        
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()