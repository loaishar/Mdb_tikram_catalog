#!/usr/bin/env python3
"""
Add Arabic translations to product names using a predefined mapping
"""
import json

# Create comprehensive translation mappings for common dairy & eggs products
translations_ar = {
    # Milk products
    "חלב מפוסטר": "حليب مبستر",
    "חלב טרי": "حليب طازج",
    "חלב הומוגני": "حليب متجانس",
    "חלב": "حليب",
    "שקית": "كيس",
    "בקבוק": "زجاجة",
    "קרטון": "كرتون",
    "בקרטון": "في كرتون",
    "מהדרין": "مهدرين",
    "שומן": "دسم",
    
    # Cheese
    "גבינה לבנה": "جبنة بيضاء",
    "גבינה צהובה": "جبنة صفراء",
    "גבינת": "جبنة",
    "גבינה": "جبنة",
    "מגורדת": "مبشورة",
    "מגורד": "مبشور",
    "פרוס": "شرائح",
    "פרוסה": "شريحة",
    "ארוז": "معبأ",
    "חריץ": "قالب",
    
    # Yogurt
    "יוגורט": "لبن",
    "אשל": "إيشل",
    "גיל": "جيل",
    "שמנת": "قشطة",
    "להקצפה": "للخفق",
    "קציפת": "مخفوق",
    
    # Eggs
    "ביצים": "بيض",
    "ארוזות": "معبأ",
    
    # Brands
    "תנובה": "تنوفا",
    "יטבתה": "يوطفاتا",
    "שטראוס": "شتراوس",
    "טרה": "تارا",
    "מילקו": "ميلكو",
    "גד": "جاد",
    "מחלבות גד": "ألبان جاد",
    "משק צוריאל": "مزرعة تسوريئيل",
    "פיראוס": "بيريوس",
    "רמת הגולן": "رامات هجولان",
    "מחלבות רמת הגולן": "ألبان رامات هجولان",
    "נעם": "نوعام",
    "עמק": "عيمك",
    "גלבוע": "جلبوع",
    "סקי": "سكي",
    "מולר": "مولر",
    "דנונה": "دانون",
    "יופלה": "يوبليه",
    "השף הלבן": "الشيف الأبيض",
    "שופרסל": "شوبرسال",
    
    # Fruits/Flavors
    "תות": "فراولة",
    "תות שדה": "فراولة برية",
    "אפרסק": "دراق",
    "לימון": "ليمون",
    "פירות יער": "توت الغابة",
    "קוקוס": "جوز الهند",
    "אננס": "أناناس",
    "מנגו": "مانجو",
    "קיווי": "كيوي",
    "אשכולית": "جريب فروت",
    "וניל": "فانيليا",
    
    # Sizes
    "ליטר": "لتر",
    "מ\"ל": "مل",
    "גרם": "غرام",
    "ק\"ג": "كغ",
    "יחידה": "وحدة",
    "יחידות": "وحدات",
    "יח": "وحدات",
    
    # Other terms
    "ללא": "بدون",
    "גלוטן": "جلوتين",
    "לקטוז": "لاكتوز",
    "כשר": "كوشر",
    "אורגני": "عضوي",
    "במשק": "مزرعة",
    "עמיד": "طويل الأمد",
    "עמידה": "طويلة الأمد",
    "פרוביוטי": "بروبيوتيك",
    "דל": "قليل",
    "עשיר": "غني",
    "מועשר": "مدعم",
    "טבעי": "طبيعي",
    "ביו": "حيوي",
    "פלוס": "بلس",
    "לייט": "لايت",
    "זיתים": "زيتون",
    "בצל": "بصل",
    "עגבניות": "طماطم"
}

def translate_hebrew_to_arabic(hebrew_text):
    """Translate Hebrew text to Arabic using the mapping"""
    if not hebrew_text:
        return hebrew_text
    
    arabic_text = hebrew_text
    
    # Sort translations by length (longest first) to avoid partial replacements
    sorted_translations = sorted(translations_ar.items(), key=lambda x: len(x[0]), reverse=True)
    
    # Replace known terms
    for hebrew, arabic in sorted_translations:
        if arabic:  # Only replace if Arabic translation exists
            arabic_text = arabic_text.replace(hebrew, arabic)
    
    # Remove any remaining Hebrew characters
    import re
    # Keep Arabic, numbers, English letters, spaces, %, ., -, /, and common punctuation
    arabic_text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u0000-\u007F%\.\-/]+', ' ', arabic_text)
    
    # Clean up spacing
    arabic_text = ' '.join(arabic_text.split())
    
    # Handle percentage formatting
    arabic_text = re.sub(r'(\d+)%', r'\1% دسم', arabic_text)
    
    return arabic_text

def create_product_translations():
    """Create a JSON file with product translations"""
    
    # Load products
    with open('all_products_import.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Processing {len(products)} products for Arabic translations...")
    
    translations_data = []
    
    for product in products:  # Process all products
        name_he = product.get('name', '')
        brand_he = product.get('brand', '')
        
        # Translate name to Arabic
        name_ar = translate_hebrew_to_arabic(name_he)
        
        # Translate brand if needed
        brand_ar = translate_hebrew_to_arabic(brand_he) if brand_he else brand_he
        
        translation = {
            "shufersal_id": product.get('metadata', {}).get('shufersal_id'),
            "name_he": name_he,
            "name_ar": name_ar,
            "brand_he": brand_he,
            "brand_ar": brand_ar,
            "size": product.get('size', '')
        }
        
        translations_data.append(translation)
        
        if len(translations_data) % 100 == 0:
            print(f"✓ Processed {len(translations_data)} products...")
    
    # Save translations
    with open('product_translations_arabic.json', 'w', encoding='utf-8') as f:
        json.dump(translations_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved {len(translations_data)} Arabic translations to product_translations_arabic.json")
    
    return translations_data

def update_mongodb_with_arabic_translations():
    """Generate update commands for MongoDB"""
    
    with open('product_translations_arabic.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    updates = []
    
    for trans in translations:
        if trans['shufersal_id']:
            update = {
                "filter": {"metadata.shufersal_id": trans['shufersal_id']},
                "update": {
                    "$set": {
                        "name_ar": trans['name_ar'],
                        "aliases.ar": [trans['name_ar']],
                    }
                }
            }
            
            if trans['brand_ar'] and trans['brand_ar'] != trans['brand_he']:
                update["update"]["$set"]["brand_ar"] = trans['brand_ar']
            
            updates.append(update)
    
    # Save update commands
    with open('mongodb_updates_arabic.json', 'w', encoding='utf-8') as f:
        json.dump(updates, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(updates)} MongoDB update commands for Arabic")
    print("Saved to mongodb_updates_arabic.json")

if __name__ == "__main__":
    print("Creating Arabic translations for products...")
    
    # Create translations
    translations = create_product_translations()
    
    # Generate MongoDB updates
    update_mongodb_with_arabic_translations()
    
    print("\nArabic translation mapping complete!")
    print("\nSample translations:")
    for t in translations[:5]:
        print(f"  {t['name_he']} → {t['name_ar']}")