# Tikram MongoDB Product Catalog Schema

## Database: tikram_catalog

### Collections Overview

#### 1. **products** Collection
Stores unique products with deduplication by GTIN/UPC or name+brand+size combination.

**Schema:**
```javascript
{
  _id: ObjectId,
  gtin: String,              // GTIN/UPC - unique when present
  name: String,              // Product name
  brand: String,             // Brand name
  size: String,              // Package size (e.g., "1L", "45g")
  description: String,       // Product description
  category_id: ObjectId,     // Reference to categories collection
  nutrition: {               // Nutritional information
    calories: Number,
    protein_g: Number,
    fat_g: Number,
    sugar_g: Number,
    sodium_mg: Number
  },
  image_urls: [String],      // Array of product images
  aliases: {                 // Multilingual names
    en: [String],           // English aliases
    ar: [String],           // Arabic aliases
    he: [String]            // Hebrew aliases
  }
}
```

**Indexes:**
- `gtin`: Unique index for deduplication
- `name, brand, size`: Compound index for fuzzy matching
- `name, aliases.*`: Text index for multilingual search
- `category_id`: For category filtering

#### 2. **offers** Collection
Merchant-specific pricing and availability data.

**Schema:**
```javascript
{
  _id: ObjectId,
  product_id: ObjectId,      // Reference to products
  merchant_id: ObjectId,     // Reference to merchants
  price: Number,             // Current price
  stock: Number,             // Available quantity
  delivery_zones: [String],  // Service areas
  promotions: [{             // Active promotions
    type: String,           // "discount", "buy_one_get_one", etc.
    value: Number,          // Discount percentage or value
    until: Date            // Promotion end date
  }],
  timestamp: Date           // Last updated
}
```

**Indexes:**
- `product_id, merchant_id`: Compound index for fast lookups

#### 3. **categories** Collection
Product taxonomy for browsing and organization.

**Schema:**
```javascript
{
  _id: ObjectId,
  name: String,              // Category name
  parent_id: ObjectId        // Reference to parent category (null for root)
}
```

**Indexes:**
- `name`: For category search
- `parent_id`: For hierarchy traversal

#### 4. **merchants** Collection
Seller information and logistics parameters.

**Schema:**
```javascript
{
  _id: ObjectId,
  name: String,              // Merchant name
  location: {                // GeoJSON location
    type: "Point",
    coordinates: [lon, lat]
  },
  contact: {
    phone: String,
    email: String
  },
  logistics: {
    delivery_radius_km: Number,
    min_order_value: Number
  }
}
```

**Indexes:**
- `name`: For merchant search

## Deduplication Strategy

### 1. GTIN/UPC Matching
```javascript
// Check for existing product by GTIN
db.products.findOne({ gtin: "6221057014015" })
```

### 2. Fuzzy Matching (when GTIN absent)
```javascript
// Search by normalized name, brand, and size
db.products.find({
  $text: { $search: "Pepsi" },
  brand: /Pepsi/i,
  size: { $in: ["1L", "1000ml", "1 liter"] }
})
```

### 3. Multilingual Alias Handling
```javascript
// Search across all language aliases
db.products.find({
  $or: [
    { "aliases.en": "Pepsi Cola 1L" },
    { "aliases.ar": "بيبسي كولا ١ لتر" },
    { "aliases.he": "פפסי קולה 1 ליטר" }
  ]
})
```

## Common Queries

### 1. Get Product with All Offers
```javascript
db.products.aggregate([
  { $match: { name: "Pepsi Cola" } },
  { $lookup: {
      from: "offers",
      localField: "_id",
      foreignField: "product_id",
      as: "offers"
  }},
  { $lookup: {
      from: "merchants",
      localField: "offers.merchant_id",
      foreignField: "_id",
      as: "merchants"
  }}
])
```

### 2. Find Products by Category with Best Price
```javascript
db.products.aggregate([
  { $match: { category_id: ObjectId("...") } },
  { $lookup: {
      from: "offers",
      localField: "_id",
      foreignField: "product_id",
      as: "offers"
  }},
  { $addFields: {
      best_price: { $min: "$offers.price" },
      total_stock: { $sum: "$offers.stock" }
  }},
  { $match: { total_stock: { $gt: 0 } } },
  { $sort: { best_price: 1 } }
])
```

### 3. Search Products with Multilingual Support
```javascript
db.products.find({
  $text: { $search: "حليب milk חלב" }
})
```

### 4. Get Products with Active Promotions
```javascript
db.products.aggregate([
  { $lookup: {
      from: "offers",
      localField: "_id",
      foreignField: "product_id",
      as: "offers"
  }},
  { $match: {
      "offers.promotions": { $exists: true, $ne: [] },
      "offers.promotions.until": { $gte: new Date() }
  }}
])
```

## Scalability Considerations

1. **Read-Heavy Optimization**: Products collection remains lean with static data
2. **Frequent Updates**: Price/stock changes isolated to offers collection
3. **Sharding Ready**: Can shard by product_id or merchant_id if needed
4. **Extensible Design**: Schema supports additional verticals (pharmacy, restaurants)
5. **Index Strategy**: Compound indexes support common query patterns

## Implementation Status

✅ Database created: tikram_catalog
✅ Collections created with proper indexes:
   - products (with text search, GTIN, and compound indexes)
   - offers (with product-merchant compound index)
   - categories (with name and parent indexes)
   - merchants (with name index)
✅ Sample data inserted for testing
✅ Deduplication queries tested
✅ Aggregation pipelines verified