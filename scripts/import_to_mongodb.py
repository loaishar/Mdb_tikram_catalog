from paths import resolve_data, open_data
#!/usr/bin/env python3
import pandas as pd
import json
from datetime import datetime
import re
import hashlib

# MongoDB IDs from our setup
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
    
    # Common patterns for size extraction
    patterns = [
        r'(\d+\.?\d*)\s*(מ"ל|מל|ml|ML)',  # milliliters
        r'(\d+\.?\d*)\s*(ל|ליטר|L|l)',     # liters
        r'(\d+\.?\d*)\s*(ג|גרם|g|G)',      # grams
        r'(\d+\.?\d*)\s*(ק"ג|קג|kg|KG)',   # kilograms
        r'(\d+)\s*(יח|יחידות)',            # units
        r'(\d+X\d+)',                       # packs like 6X1L
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
    
    # Common brand mappings (Hebrew to English)
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
    
    # Try exact match first
    if brand in brand_mapping:
        return brand_mapping[brand]
    
    # Try partial match
    for hebrew, english in brand_mapping.items():
        if hebrew in brand:
            return english
    
    # Return original if no mapping found
    return brand

def parse_unit_price(unit_price_str):
    """Parse unit price string to extract price and unit"""
    if not unit_price_str:
        return None, None
    
    # Pattern: "0.64 ש"ח ל- 100 מ"ל"
    pattern = r'([\d.]+)\s*ש"ח\s*ל-?\s*([\d.]+)\s*(.+)'
    match = re.match(pattern, str(unit_price_str))
    
    if match:
        price = float(match.group(1))
        quantity = float(match.group(2))
        unit = match.group(3).strip()
        return price, f"{quantity} {unit}"
    
    return None, None

def generate_shufersal_id_mapping(product_id):
    """Generate a unique ID based on Shufersal product ID"""
    if not product_id:
        return None
    # Create a hash based on the Shufersal ID to ensure uniqueness
    hash_obj = hashlib.md5(str(product_id).encode())
    return f"shufersal_{product_id}"

def process_health_labels(labels_str):
    """Process health labels into array"""
    if pd.isna(labels_str) or not labels_str:
        return []
    
    # Split by common separators
    labels = re.split(r'[,،،]', str(labels_str))
    return [label.strip() for label in labels if label.strip()]

def create_product_document(row):
    """Create a product document from Excel row"""
    # Extract and clean data
    product_name = clean_text(row['שם המוצר'])
    brand = normalize_brand(row['מותג'])
    size = extract_size_from_text(row['גודל/כמות'])
    
    # Create aliases in different languages
    aliases = {
        "he": [product_name],  # Original Hebrew name
        "en": [],  # Will be populated if we have translations
        "ar": []   # Will be populated if we have translations
    }
    
    # Add brand to product name if not already included
    if brand and brand not in product_name:
        aliases["he"].append(f"{product_name} {row['מותג']}")
    
    # Create the product document
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
    
    # Check if product is on sale
    promotions = []
    if row['מבצע'] == 'מבצע':
        promotions.append({
            "type": "sale",
            "description": "מבצע",
            "until": {"$date": "2025-01-31T00:00:00Z"}
        })
    
    offer = {
        "product_id": {"$oid": product_id},
        "merchant_id": {"$oid": TIKRAM_SHOP_MERCHANT_ID},
        "price": price,
        "stock": 0 if row['זמינות'] == 'חסר במלאי' else 100,  # Default stock
        "delivery_zones": ["Tel Aviv", "Jerusalem", "Haifa", "Center"],
        "promotions": promotions,
        "unit_price_info": clean_text(row['מחיר ליחידה']),
        "timestamp": {"$date": datetime.now().isoformat() + "Z"}
    }
    
    return offer

def main():
    """Main import function"""
    file_path = "./חלב_וביצים_shufersal_with_images.xlsx"
    
    print(f"Loading Excel file: {file_path}")
    df = pd.read_excel(file_path)
    
    print(f"Processing {len(df)} products...")
    
    products_to_import = []
    offers_to_import = []
    
    # Process each row
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"Processing row {idx}/{len(df)}...")
        
        try:
            # Create product document
            product = create_product_document(row)
            
            # Generate a temporary product ID (will be replaced by MongoDB)
            temp_product_id = generate_shufersal_id_mapping(row['מזהה מוצר'])
            
            # Create offer document
            offer = create_offer_document(row, temp_product_id)
            
            products_to_import.append(product)
            offers_to_import.append(offer)
            
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    # Save to JSON files for MongoDB import
    print(f"\nPrepared {len(products_to_import)} products and {len(offers_to_import)} offers")
    
    with open_data('products_import.json', 'w', encoding='utf-8') as f:
        json.dump(products_to_import, f, ensure_ascii=False, indent=2)
    
    with open_data('offers_import.json', 'w', encoding='utf-8') as f:
        json.dump(offers_to_import, f, ensure_ascii=False, indent=2)
    
    print("\nExport complete!")
    print("- products_import.json created")
    print("- offers_import.json created")
    
    # Print summary statistics
    print("\n=== Import Summary ===")
    print(f"Total products: {len(products_to_import)}")
    print(f"Total offers: {len(offers_to_import)}")
    
    # Brand distribution
    brands = [p.get('brand') for p in products_to_import if p.get('brand')]
    brand_counts = pd.Series(brands).value_counts()
    print(f"\nTop 10 brands:")
    for brand, count in brand_counts.head(10).items():
        print(f"  {brand}: {count} products")
    
    # Products with images
    with_images = sum(1 for p in products_to_import if p.get('image_urls'))
    print(f"\nProducts with images: {with_images}/{len(products_to_import)}")
    
    # Products on sale
    on_sale = sum(1 for o in offers_to_import if o.get('promotions'))
    print(f"Products on sale: {on_sale}/{len(offers_to_import)}")

if __name__ == "__main__":
    main()
