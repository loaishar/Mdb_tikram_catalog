#!/usr/bin/env python3
"""
Create offers for all 928 imported products
"""
import json
import pandas as pd
from datetime import datetime

# MongoDB IDs
TIKRAM_SHOP_MERCHANT_ID = "68bf06365371c586220eb9f7"

def create_offers_for_all_products():
    """Create offers for all products based on Excel data"""
    # Load the original Excel file to get price information
    df = pd.read_excel("./חלב_וביצים_shufersal_with_images.xlsx")
    
    # Load the product ID mapping to know which products were imported
    with open('product_id_mapping.json', 'r', encoding='utf-8') as f:
        product_mapping = json.load(f)
    
    print(f"Creating offers for {len(product_mapping)} products...")
    
    all_offers = []
    
    # Process each product in the Excel
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"Processing offer {idx}/{len(df)}...")
        
        shufersal_id = str(row['מזהה מוצר']).strip() if pd.notna(row['מזהה מוצר']) else None
        
        if not shufersal_id:
            continue
            
        # Create offer document
        offer = {
            "shufersal_id": shufersal_id,  # Store for mapping later
            "merchant_id": {"$oid": TIKRAM_SHOP_MERCHANT_ID},
            "price": float(row['מחיר ₪']) if pd.notna(row['מחיר ₪']) else 0,
            "stock": 0 if row['זמינות'] == 'חסר במלאי' else 100,
            "delivery_zones": ["Tel Aviv", "Jerusalem", "Haifa", "Center", "North", "South"],
            "promotions": [],
            "unit_price_info": str(row['מחיר ליחידה']) if pd.notna(row['מחיר ליחידה']) else "",
            "timestamp": {"$date": datetime.now().isoformat() + "Z"}
        }
        
        # Add promotion if applicable
        if pd.notna(row['מבצע']) and row['מבצע'] == 'מבצע':
            offer["promotions"].append({
                "type": "sale",
                "description": "מבצע שופרסל",
                "until": {"$date": "2025-01-31T00:00:00Z"}
            })
        
        all_offers.append(offer)
    
    print(f"\nCreated {len(all_offers)} offers")
    
    # Split offers into batches for import
    batch_size = 100
    offer_batches = []
    
    for i in range(0, len(all_offers), batch_size):
        batch = all_offers[i:i+batch_size]
        offer_batches.append(batch)
    
    print(f"Split into {len(offer_batches)} batches of {batch_size} offers each")
    
    # Save offer batches
    for i, batch in enumerate(offer_batches):
        filename = f'offers_batch_{i+1}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
        print(f"Saved batch {i+1} to {filename} ({len(batch)} offers)")
    
    # Summary statistics
    print("\n=== Offers Summary ===")
    print(f"Total offers created: {len(all_offers)}")
    
    # Price statistics
    prices = [o['price'] for o in all_offers if o['price'] > 0]
    if prices:
        print(f"Average price: ₪{sum(prices)/len(prices):.2f}")
        print(f"Min price: ₪{min(prices)}")
        print(f"Max price: ₪{max(prices)}")
    
    # Promotions
    on_sale = sum(1 for o in all_offers if o.get('promotions'))
    print(f"Products on sale: {on_sale}/{len(all_offers)} ({on_sale*100/len(all_offers):.1f}%)")
    
    # Stock status
    in_stock = sum(1 for o in all_offers if o['stock'] > 0)
    print(f"Products in stock: {in_stock}/{len(all_offers)} ({in_stock*100/len(all_offers):.1f}%)")
    
    # Save offer status
    status = {
        "total_offers": len(all_offers),
        "batch_count": len(offer_batches),
        "offers_with_promotions": on_sale,
        "offers_in_stock": in_stock,
        "timestamp": datetime.now().isoformat() + "Z"
    }
    
    with open('offers_import_status.json', 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    print("\nOffers ready for import!")
    
    return all_offers

if __name__ == "__main__":
    create_offers_for_all_products()