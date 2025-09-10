#!/usr/bin/env python3
"""
Prepare all products for MongoDB import with proper ObjectId format
"""
import json
import pandas as pd
from datetime import datetime
import re
import hashlib

# MongoDB IDs
TIKRAM_SHOP_MERCHANT_ID = "68bf06365371c586220eb9f7"
DAIRY_EGGS_CATEGORY_ID = "68bef17f5371c586220eb9ea"

def clean_text(text):
    """Clean and normalize text fields"""
    if pd.isna(text) or text is None:
        return None
    return str(text).strip()

def extract_size_from_text(text):
    """Extract size/quantity from text"""
    if not text:
        return None
    
    patterns = [
        r'(\d+\.?\d*)\s*(מ"ל|מל|ml|ML)',
        r'(\d+\.?\d*)\s*(ל|ליטר|L|l)',
        r'(\d+\.?\d*)\s*(ג|גרם|g|G)',
        r'(\d+\.?\d*)\s*(ק"ג|קג|kg|KG)',
        r'(\d+)\s*(יח|יחידות)',
        r'(\d+X\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return text

def normalize_brand(brand_name):
    """Normalize and translate brand names"""
    if not brand_name:
        return None
    
    brand = clean_text(brand_name)
    
    brand_mapping = {
        'תנובה': 'Tnuva',
        'יטבתה': 'Yotvata',
        'שטראוס': 'Strauss',
        'טרה': 'Tara',
        'מילקו': 'Milco',
        'גד': 'Gad',
        'משק צוריאל': 'Meshek Tzuriel',
        'פיראוס': 'Piraeus',
        'גל': 'Gal',
        'נועם': 'Noam',
        'מחלבות גד': 'Gad Dairy',
        'משק שטראוס': 'Strauss Farm',
        'עוף טוב': 'Of Tov',
        'יש': 'Yesh',
        'מאיר': 'Meir',
        'פרי הדר': 'Pri Hadar',
        'רמת הגולן': 'Ramat HaGolan',
        'החקלאית': 'HaHakla\'it',
        'טעם הטבע': 'Taam HaTeva',
        'בייבי ביס': 'Baby Bis',
        'גבינת העמק': 'Gvinat HaEmek',
        'שופרסל': 'Shufersal',
        'מעדני צפת': 'Maadanei Tzfat'
    }
    
    if brand in brand_mapping:
        return brand_mapping[brand]
    
    for hebrew, english in brand_mapping.items():
        if hebrew in brand:
            return english
    
    return brand

def process_health_labels(labels_str):
    """Process health labels into array"""
    if pd.isna(labels_str) or not labels_str:
        return []
    
    labels = re.split(r'[,،،]', str(labels_str))
    return [label.strip() for label in labels if label.strip()]

def create_product_document(row):
    """Create a product document from Excel row"""
    product_name = clean_text(row['שם המוצר'])
    brand = normalize_brand(row['מותג'])
    size = extract_size_from_text(row['גודל/כמות'])
    
    aliases = {
        "he": [product_name],
        "en": [],
        "ar": []
    }
    
    if brand and brand not in product_name:
        aliases["he"].append(f"{product_name} {row['מותג']}")
    
    product = {
        "name": product_name,
        "brand": brand,
        "size": size,
        "description": f"{product_name} - {brand}" if brand else product_name,
        "category_id": {"$oid": DAIRY_EGGS_CATEGORY_ID},
        "image_urls": [row['קישור לתמונה']] if pd.notna(row['קישור לתמונה']) else [],
        "aliases": aliases,
        "metadata": {
            "shufersal_id": clean_text(row['מזהה מוצר']),
            "kosher": clean_text(row['כשר']),
            "health_labels": process_health_labels(row['תוויות בריאות']),
            "sales_method": clean_text(row['אופן מכירה']),
            "imported_at": {"$date": datetime.now().isoformat() + "Z"}
        }
    }
    
    # Remove None values
    product = {k: v for k, v in product.items() if v is not None}
    
    return product

def create_offer_document(row, product_id):
    """Create an offer document from Excel row"""
    price = float(row['מחיר ₪']) if pd.notna(row['מחיר ₪']) else 0
    
    promotions = []
    if row['מבצע'] == 'מבצע':
        promotions.append({
            "type": "sale",
            "description": "מבצע שופרסל",
            "until": {"$date": "2025-01-31T00:00:00Z"}
        })
    
    offer = {
        "product_id": {"$oid": product_id},
        "merchant_id": {"$oid": TIKRAM_SHOP_MERCHANT_ID},
        "price": price,
        "stock": 0 if row['זמינות'] == 'חסר במלאי' else 100,
        "delivery_zones": ["Tel Aviv", "Jerusalem", "Haifa", "Center", "North", "South"],
        "promotions": promotions,
        "unit_price_info": clean_text(row['מחיר ליחידה']),
        "timestamp": {"$date": datetime.now().isoformat() + "Z"}
    }
    
    return offer

def prepare_full_import():
    """Prepare all 928 products for MongoDB import"""
    file_path = "./חלב_וביצים_shufersal_with_images.xlsx"
    
    print(f"Loading Excel file: {file_path}")
    df = pd.read_excel(file_path)
    
    print(f"Processing {len(df)} products...")
    
    all_products = []
    product_id_mapping = {}
    
    # Process each row
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"Processing row {idx}/{len(df)}...")
        
        try:
            # Create product document
            product = create_product_document(row)
            
            # Store the mapping for later use with offers
            shufersal_id = clean_text(row['מזהה מוצר'])
            product_id_mapping[shufersal_id] = len(all_products)  # Index in array
            
            all_products.append(product)
            
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    print(f"\nPrepared {len(all_products)} products for import")
    
    # Save as single file for MongoDB import
    with open('all_products_import.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    
    print("Saved to all_products_import.json")
    
    # Also save the mapping for offer creation
    with open('product_id_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(product_id_mapping, f, ensure_ascii=False, indent=2)
    
    print("Saved product ID mapping to product_id_mapping.json")
    
    # Print summary
    print("\n=== Import Summary ===")
    print(f"Total products: {len(all_products)}")
    
    # Brand distribution
    brands = {}
    for p in all_products:
        brand = p.get('brand', 'Unknown')
        brands[brand] = brands.get(brand, 0) + 1
    
    print("\nTop 10 brands:")
    for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {brand}: {count} products")
    
    print(f"\nProducts with images: {sum(1 for p in all_products if p.get('image_urls'))}")
    
    return all_products, df

if __name__ == "__main__":
    prepare_full_import()