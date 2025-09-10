#!/usr/bin/env python3
"""
Add English translations to product names using a predefined mapping
"""
import json

# Create comprehensive translation mappings for common dairy & eggs products
translations = {
    # Milk products
    "חלב מפוסטר": "Pasteurized Milk",
    "חלב טרי": "Fresh Milk",
    "חלב הומוגני": "Homogenized Milk",
    "חלב": "Milk",
    "שקית": "Bag",
    "בקבוק": "Bottle",
    "קרטון": "Carton",
    "בקרטון": "in Carton",
    "מהדרין": "Mehadrin",
    "שומן": "Fat",
    
    # Cheese
    "גבינה לבנה": "White Cheese",
    "גבינה צהובה": "Yellow Cheese",
    "גבינת": "Cheese",
    "גבינה": "Cheese",
    "מגורדת": "Shredded",
    "מגורד": "Shredded",
    "פרוס": "Sliced",
    "פרוסה": "Sliced",
    "ארוז": "Packaged",
    "חריץ": "Block",
    
    # Yogurt
    "יוגורט": "Yogurt",
    "אשל": "Eshel",
    "גיל": "Gil",
    "שמנת": "Cream",
    "להקצפה": "Whipping",
    "קציפת": "Whipped",
    
    # Eggs
    "ביצים": "Eggs",
    "ארוזות": "Packaged",
    
    # Brands
    "תנובה": "Tnuva",
    "יטבתה": "Yotvata",
    "שטראוס": "Strauss",
    "טרה": "Tara",
    "מילקו": "Milco",
    "גד": "Gad",
    "מחלבות גד": "Gad Dairy",
    "משק צוריאל": "Meshek Tzuriel",
    "פיראוס": "Piraeus",
    "רמת הגולן": "Ramat HaGolan",
    "מחלבות רמת הגולן": "Ramat HaGolan Dairy",
    "נעם": "Noam",
    "עמק": "Emek",
    "גלבוע": "Gilboa",
    "סקי": "Ski",
    "מולר": "Muller",
    "דנונה": "Danone",
    "יופלה": "Yoplait",
    "השף הלבן": "The White Chef",
    "שופרסל": "Shufersal",
    
    # Fruits/Flavors
    "תות": "Strawberry",
    "תות שדה": "Wild Strawberry",
    "אפרסק": "Peach",
    "לימון": "Lemon",
    "פירות יער": "Forest Fruits",
    "קוקוס": "Coconut",
    "אננס": "Pineapple",
    "מנגו": "Mango",
    "קיווי": "Kiwi",
    "אשכולית": "Grapefruit",
    "וניל": "Vanilla",
    
    # Sizes
    "ליטר": "Liter",
    "מ\"ל": "ml",
    "גרם": "g",
    "ק\"ג": "kg",
    "יחידה": "unit",
    "יחידות": "units",
    "יח": "units",
    
    # Other terms
    "ללא": "Without",
    "גלוטן": "Gluten",
    "לקטוז": "Lactose",
    "כשר": "Kosher",
    "אורגני": "Organic",
    "במשק": "Farm",
    "עמיד": "Long Life",
    "עמידה": "Long Life",
    "פרוביוטי": "Probiotic",
    "דל": "Low",
    "עשיר": "Rich",
    "מועשר": "Enriched",
    "טבעי": "Natural",
    "ביו": "Bio",
    "פלוס": "Plus",
    "לייט": "Light",
    "זיתים": "Olives",
    "בצל": "Onion",
    "עגבניות": "Tomatoes"
}

def translate_hebrew_to_english(hebrew_text):
    """Translate Hebrew text to English using the mapping"""
    if not hebrew_text:
        return hebrew_text
    
    english_text = hebrew_text
    
    # Sort translations by length (longest first) to avoid partial replacements
    sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
    
    # Replace known terms
    for hebrew, english in sorted_translations:
        if english:  # Only replace if English translation exists
            english_text = english_text.replace(hebrew, english)
    
    # Remove any remaining Hebrew characters
    import re
    # Keep numbers, English letters, spaces, %, ., -, /, and common punctuation
    english_text = re.sub(r'[^\u0000-\u007F%\.\-/]+', ' ', english_text)
    
    # Clean up spacing
    english_text = ' '.join(english_text.split())
    
    return english_text

def create_product_translations():
    """Create a JSON file with product translations"""
    
    # Load products
    with open('all_products_import.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Processing {len(products)} products...")
    
    translations_data = []
    
    for product in products:  # Process all products
        name_he = product.get('name', '')
        brand_he = product.get('brand', '')
        
        # Translate name
        name_en = translate_hebrew_to_english(name_he)
        
        # Clean up percentages
        import re
        name_en = re.sub(r'(\d+)%', r'\1% Fat', name_en)
        
        # Translate brand if needed
        brand_en = translate_hebrew_to_english(brand_he) if brand_he else brand_he
        
        translation = {
            "shufersal_id": product.get('metadata', {}).get('shufersal_id'),
            "name_he": name_he,
            "name_en": name_en,
            "brand_he": brand_he,
            "brand_en": brand_en,
            "size": product.get('size', '')
        }
        
        translations_data.append(translation)
        
        if len(translations_data) % 100 == 0:
            print(f"✓ Processed {len(translations_data)} products...")
    
    # Save translations
    with open('product_translations.json', 'w', encoding='utf-8') as f:
        json.dump(translations_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved {len(translations_data)} translations to product_translations.json")
    
    return translations_data

def update_mongodb_with_translations():
    """Generate update commands for MongoDB"""
    
    with open('product_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    updates = []
    
    for trans in translations:
        if trans['shufersal_id']:
            update = {
                "filter": {"metadata.shufersal_id": trans['shufersal_id']},
                "update": {
                    "$set": {
                        "name_en": trans['name_en'],
                        "aliases.en": [trans['name_en']],
                    }
                }
            }
            
            if trans['brand_en'] and trans['brand_en'] != trans['brand_he']:
                update["update"]["$set"]["brand_en"] = trans['brand_en']
            
            updates.append(update)
    
    # Save update commands
    with open('mongodb_updates.json', 'w', encoding='utf-8') as f:
        json.dump(updates, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(updates)} MongoDB update commands")
    print("Saved to mongodb_updates.json")

if __name__ == "__main__":
    print("Creating English translations for products...")
    
    # Create translations
    translations = create_product_translations()
    
    # Generate MongoDB updates
    update_mongodb_with_translations()
    
    print("\nTranslation mapping complete!")
    print("\nSample translations:")
    for t in translations[:5]:
        print(f"  {t['name_he']} → {t['name_en']}")