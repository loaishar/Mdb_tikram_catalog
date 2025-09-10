from paths import resolve_data, open_data
#!/usr/bin/env python3
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any
import re
import hashlib
import uuid

def clean_text(text):
    """Clean and normalize text fields"""
    if pd.isna(text) or text is None:
        return None
    return str(text).strip()

def extract_size_from_name(product_name):
    """Extract size/quantity from product name"""
    if not product_name:
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
        match = re.search(pattern, product_name)
        if match:
            return match.group(0)
    return None

def normalize_brand(brand_name):
    """Normalize brand names for consistency"""
    if not brand_name:
        return None
    
    brand = clean_text(brand_name)
    # Common brand normalizations
    brand_mapping = {
        'תנובה': 'Tnuva',
        'יטבתה': 'Yotvata',
        'שטראוס': 'Strauss',
        'טרה': 'Tara',
        'מילקו': 'Milco',
        'גד': 'Gad',
        'משק צוריאל': 'Meshek Tzuriel',
        'פיראוס': 'Piraeus'
    }
    
    for hebrew, english in brand_mapping.items():
        if hebrew in brand:
            return english
    
    return brand

def analyze_excel_structure(file_path):
    """Read and analyze the Excel file structure"""
    print(f"Reading Excel file: {file_path}")
    
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    print(f"\nDataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nColumn names:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: {col}")
    
    print("\nFirst 3 rows sample:")
    print(df.head(3).to_dict('records'))
    
    print("\nData types:")
    print(df.dtypes)
    
    print("\nNull values count:")
    print(df.isnull().sum())
    
    print("\nUnique values in key columns:")
    for col in df.columns[:10]:  # First 10 columns
        unique_count = df[col].nunique()
        print(f"  {col}: {unique_count} unique values")
        if unique_count <= 5:
            print(f"    Values: {df[col].unique()[:5]}")
    
    return df

def map_to_mongodb_schema(df):
    """Map Excel data to MongoDB schema"""
    products = []
    offers = []
    
    # Analyze column mappings
    column_mapping = {
        'product_name': None,
        'brand': None,
        'price': None,
        'barcode': None,
        'image_url': None,
        'description': None,
        'category': None,
        'unit_price': None,
        'quantity': None
    }
    
    # Try to identify columns by content
    for col in df.columns:
        col_lower = col.lower()
        sample_data = df[col].dropna().head(5)
        
        if any(keyword in col_lower for keyword in ['name', 'שם', 'product']):
            column_mapping['product_name'] = col
        elif any(keyword in col_lower for keyword in ['brand', 'מותג', 'יצרן']):
            column_mapping['brand'] = col
        elif any(keyword in col_lower for keyword in ['price', 'מחיר']) and 'unit' not in col_lower:
            column_mapping['price'] = col
        elif any(keyword in col_lower for keyword in ['barcode', 'ברקוד', 'gtin', 'upc', 'ean']):
            column_mapping['barcode'] = col
        elif any(keyword in col_lower for keyword in ['image', 'תמונה', 'img']):
            column_mapping['image_url'] = col
        elif any(keyword in col_lower for keyword in ['description', 'תיאור']):
            column_mapping['description'] = col
        elif any(keyword in col_lower for keyword in ['unit', 'יחידה']) and 'price' in col_lower:
            column_mapping['unit_price'] = col
        elif any(keyword in col_lower for keyword in ['quantity', 'כמות']):
            column_mapping['quantity'] = col
    
    print("\nIdentified column mappings:")
    for key, value in column_mapping.items():
        if value:
            print(f"  {key}: {value}")
    
    return column_mapping, df

def generate_product_id():
    """Generate a MongoDB ObjectId-like string"""
    return str(uuid.uuid4().hex[:24])

# Main execution
if __name__ == "__main__":
    file_path = "./חלב_וביצים_shufersal_with_images.xlsx"
    
    # Analyze the Excel structure
    df = analyze_excel_structure(file_path)
    
    # Map to MongoDB schema
    column_mapping, data = map_to_mongodb_schema(df)
