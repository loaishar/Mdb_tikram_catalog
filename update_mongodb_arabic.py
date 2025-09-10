#!/usr/bin/env python3
"""
Update MongoDB with Arabic translations
"""
import json

def create_arabic_batch_updates():
    """Create batch update script for MongoDB using MCP tools"""
    
    # Load Arabic translations
    with open('product_translations_arabic.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    print(f"Loaded {len(translations)} Arabic translations")
    
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
                            "name_ar": trans['name_ar'],
                            "aliases.ar": [trans['name_ar']]
                        }
                    }
                }
                
                if trans['brand_ar'] and trans['brand_ar'] != trans['brand_he']:
                    update["update"]["$set"]["brand_ar"] = trans['brand_ar']
                
                batch_updates.append(update)
        
        batches.append(batch_updates)
    
    print(f"Created {len(batches)} batches of Arabic updates")
    
    # Save batches to separate files
    for i, batch in enumerate(batches):
        filename = f'arabic_update_batch_{i+1}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
        print(f"Saved batch {i+1} with {len(batch)} updates to {filename}")
    
    return batches

if __name__ == "__main__":
    print("Creating MongoDB Arabic update batches...")
    batches = create_arabic_batch_updates()
    print(f"\nTotal Arabic updates created: {sum(len(b) for b in batches)}")
    print("\nArabic update batches ready for MongoDB!")