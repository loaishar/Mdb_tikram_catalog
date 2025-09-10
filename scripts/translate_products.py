from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Translate Hebrew product names to English and update MongoDB
"""
from pymongo import MongoClient
from googletrans import Translator
import time
import json

# MongoDB connection
CONNECTION_STRING = "mongodb+srv://luaysharqiya_db_user:1yfBzVW8czpXussR@clustertikramcatalog.kwkrm7n.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTikramCatalog"

# Initialize
client = MongoClient(CONNECTION_STRING)
db = client.tikram_catalog
products_collection = db.products

# Initialize translator (using googletrans instead of Google Cloud for simplicity)
translator = Translator()

def translate_batch(texts, target='en', source='he'):
    """Translate a batch of texts"""
    translations = []
    for text in texts:
        try:
            result = translator.translate(text, dest=target, src=source)
            translations.append(result.text)
            time.sleep(0.1)  # Rate limiting
        except Exception as e:
            print(f"Translation error for '{text}': {e}")
            translations.append(text)  # Keep original if translation fails
    return translations

def update_products_with_translations():
    """Update all products with English translations"""
    
    # Get all products
    products = list(products_collection.find(
        {"metadata.shufersal_id": {"$exists": True}},
        {"_id": 1, "name": 1, "brand": 1, "description": 1, "aliases": 1}
    ).limit(10))  # Start with 10 for testing
    
    print(f"Found {len(products)} products to translate")
    
    for i, product in enumerate(products):
        if i % 10 == 0:
            print(f"Processing product {i+1}/{len(products)}")
        
        try:
            # Translate product name
            name_he = product.get('name', '')
            if name_he:
                name_en = translator.translate(name_he, dest='en', src='he').text
                
                # Update the product with English name
                update_doc = {
                    "$set": {
                        "name_en": name_en,
                        "aliases.en": [name_en]  # Add to English aliases
                    }
                }
                
                # If brand needs translation
                brand = product.get('brand', '')
                if brand and any(ord(c) > 127 for c in brand):  # Has non-ASCII chars
                    brand_en = translator.translate(brand, dest='en', src='he').text
                    update_doc["$set"]["brand_en"] = brand_en
                
                # Update the document
                result = products_collection.update_one(
                    {"_id": product["_id"]},
                    update_doc
                )
                
                if result.modified_count > 0:
                    print(f"✓ Updated: {name_he} → {name_en}")
                
                time.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            print(f"Error processing product {product.get('_id')}: {e}")
            continue
    
    print("\nTranslation complete!")

def verify_translations():
    """Verify some translated products"""
    print("\n=== Verification ===")
    
    # Get some products with translations
    sample = products_collection.find(
        {"name_en": {"$exists": True}},
        {"name": 1, "name_en": 1, "brand": 1, "brand_en": 1}
    ).limit(5)
    
    for product in sample:
        print(f"\nHebrew: {product.get('name')}")
        print(f"English: {product.get('name_en')}")
        if product.get('brand_en'):
            print(f"Brand: {product.get('brand')} → {product.get('brand_en')}")

if __name__ == "__main__":
    print("Starting product translation...")
    print(f"Database: tikram_catalog")
    print(f"Collection: products")
    
    # Run translation
    update_products_with_translations()
    
    # Verify results
    verify_translations()
    
    # Close connection
    client.close()
    print("\nDone!")
