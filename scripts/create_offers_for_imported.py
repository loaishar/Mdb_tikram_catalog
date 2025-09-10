from paths import resolve_data, open_data
#!/usr/bin/env python3
"""
Create offers for imported products based on the original Excel data
"""
import json
import pandas as pd

# MongoDB IDs
TIKRAM_SHOP_MERCHANT_ID = "68bf06365371c586220eb9f7"

# Product IDs from the import (first 5 products)
imported_product_ids = {
    "P_42015": "68bf07085371c586220eb9f8",  # חלב מפוסטר3% מהדרין שקית
    "P_42435": "68bf07085371c586220eb9f9",  # חלב מפוסטר 1% בקרטון
    "P_56845": "68bf07085371c586220eb9fa",  # חלב טרי הומוגני 3% קרטון
    "P_4131074": "68bf07085371c586220eb9fb",  # חלב בקרטון 3% שומן
    "P_42411": "68bf07085371c586220eb9fc",  # חלב בקבוק 3% יטבתה
}

def create_offers_for_products():
    """Create offers based on original Excel data"""
    # Load original Excel file to get prices
    df = pd.read_excel("./חלב_וביצים_shufersal_with_images.xlsx")
    
    offers = []
    
    for shufersal_id, mongo_id in imported_product_ids.items():
        # Find the product in the Excel data
        product_row = df[df['מזהה מוצר'] == shufersal_id]
        
        if not product_row.empty:
            row = product_row.iloc[0]
            
            # Create offer document
            offer = {
                "product_id": {"$oid": mongo_id},
                "merchant_id": {"$oid": TIKRAM_SHOP_MERCHANT_ID},
                "price": float(row['מחיר ₪']),
                "stock": 0 if row['זמינות'] == 'חסר במלאי' else 100,
                "delivery_zones": ["Tel Aviv", "Jerusalem", "Haifa", "Center", "North", "South"],
                "promotions": [],
                "unit_price_info": str(row['מחיר ליחידה']),
                "timestamp": {"$date": "2025-01-09T00:00:00Z"}
            }
            
            # Add promotion if applicable
            if row['מבצע'] == 'מבצע':
                offer["promotions"].append({
                    "type": "sale",
                    "description": "מבצע שופרסל",
                    "until": {"$date": "2025-01-31T00:00:00Z"}
                })
            
            offers.append(offer)
            print(f"Created offer for {shufersal_id}: ₪{offer['price']}")
    
    # Save offers for import
    with open_data('offers_batch_1.json', 'w', encoding='utf-8') as f:
        json.dump(offers, f, ensure_ascii=False, indent=2)
    
    print(f"\nCreated {len(offers)} offers")
    print("Saved to offers_batch_1.json")
    
    return offers

if __name__ == "__main__":
    create_offers_for_products()
