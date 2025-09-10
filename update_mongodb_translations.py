#!/usr/bin/env python3
"""
Update MongoDB with English translations and empty Arabic arrays
"""
import json

def create_batch_updates():
    """Create batch update script for MongoDB using MCP tools"""
    
    # Load translations
    with open('product_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    print(f"Loaded {len(translations)} translations")
    
    # Create updates in batches
    batch_size = 50
    batches = []
    
    for i in range(0, len(translations), batch_size):
        batch = translations[i:i+batch_size]
        batch_updates = []
        
        for trans in batch:
            if trans['shufersal_id']:
                update = {
                    "filter": {"metadata.shufersal_id": trans['shufersal_id']},
                    "update": {
                        "$set": {
                            "name_en": trans['name_en'],
                            "aliases.en": [trans['name_en']],
                            "aliases.ar": []  # Empty Arabic array
                        }
                    }
                }
                
                if trans['brand_en'] and trans['brand_en'] != trans['brand_he']:
                    update["update"]["$set"]["brand_en"] = trans['brand_en']
                
                batch_updates.append(update)
        
        batches.append(batch_updates)
    
    print(f"Created {len(batches)} batches of updates")
    
    # Save batches to separate files
    for i, batch in enumerate(batches):
        filename = f'update_batch_{i+1}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
        print(f"Saved batch {i+1} with {len(batch)} updates to {filename}")
    
    return batches

if __name__ == "__main__":
    print("Creating MongoDB update batches...")
    batches = create_batch_updates()
    print(f"\nTotal updates created: {sum(len(b) for b in batches)}")
    print("\nUpdate batches ready for MongoDB!")