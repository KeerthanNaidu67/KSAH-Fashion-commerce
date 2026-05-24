"""
Seed script — populates the database with demo data.
Run: python database/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
import random
from database.db import db_instance
from models.user import User
from models.product import Product
from models.order import Order
from models.review import Review

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/fashion_ecommerce')

PRODUCTS_DATA = [
    # Men
    {'name': 'Classic White Oxford Shirt', 'brand': 'Zara', 'category': 'Men', 'price': 299, 'original_price': 399,
     'description': 'Timeless white Oxford shirt crafted from premium cotton. Perfect for formal and smart-casual occasions.',
     'sizes': ['S', 'M', 'L', 'XL'], 'colors': ['White', 'Blue'], 'stock': 45,
     'images': ['https://images.unsplash.com/photo-1620012253295-c15cc3e65df4?w=600'],
     'tags': ['shirt', 'formal', 'cotton'], 'is_featured': True},
    {'name': 'Slim Fit Chino Trousers', 'brand': 'H&M', 'category': 'Men', 'price': 199, 'original_price': 249,
     'description': 'Modern slim-fit chinos in stretch fabric. Versatile for office and weekend.',
     'sizes': ['S', 'M', 'L', 'XL', 'XXL'], 'colors': ['Beige', 'Navy', 'Black'], 'stock': 30,
     'images': ['https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600'],
     'tags': ['trousers', 'chino', 'slim'], 'is_featured': True},
    {'name': 'Premium Denim Jacket', 'brand': 'Levi\'s', 'category': 'Men', 'price': 549, 'original_price': 699,
     'description': 'Vintage-wash denim jacket with classic trucker styling. An essential wardrobe staple.',
     'sizes': ['S', 'M', 'L', 'XL'], 'colors': ['Light Blue', 'Dark Blue'], 'stock': 20,
     'images': ['https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=600'],
     'tags': ['jacket', 'denim', 'casual'], 'is_featured': True},
    {'name': 'Merino Wool Sweater', 'brand': 'Uniqlo', 'category': 'Men', 'price': 349, 'original_price': 349,
     'description': 'Luxuriously soft merino wool crew-neck sweater. Fine gauge knit for year-round comfort.',
     'sizes': ['XS', 'S', 'M', 'L', 'XL'], 'colors': ['Camel', 'Grey', 'Navy'], 'stock': 25,
     'images': ['https://images.unsplash.com/photo-1594938298603-c8148c4b4e2f?w=600'],
     'tags': ['sweater', 'wool', 'premium'], 'is_featured': False},
    {'name': 'Tailored Suit Blazer', 'brand': 'Massimo Dutti', 'category': 'Men', 'price': 1299, 'original_price': 1599,
     'description': 'Italian-style blazer with structured shoulders and clean lines. Elevate any outfit.',
     'sizes': ['S', 'M', 'L', 'XL'], 'colors': ['Charcoal', 'Navy', 'Black'], 'stock': 12,
     'images': ['https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600'],
     'tags': ['blazer', 'formal', 'suit'], 'is_featured': True},

    # Women
    {'name': 'Floral Midi Dress', 'brand': 'Zara', 'category': 'Women', 'price': 399, 'original_price': 499,
     'description': 'Elegant floral midi dress with a flattering A-line silhouette. Perfect for summer occasions.',
     'sizes': ['XS', 'S', 'M', 'L'], 'colors': ['Floral Print'], 'stock': 35,
     'images': ['https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600'],
     'tags': ['dress', 'floral', 'midi', 'summer'], 'is_featured': True},
    {'name': 'High-Waist Tailored Trousers', 'brand': 'H&M', 'category': 'Women', 'price': 249, 'original_price': 299,
     'description': 'Sophisticated wide-leg trousers with a high waist and clean silhouette.',
     'sizes': ['XS', 'S', 'M', 'L', 'XL'], 'colors': ['Black', 'Cream', 'Camel'], 'stock': 28,
     'images': ['https://images.unsplash.com/photo-1594938374182-a57d57a8d574?w=600'],
     'tags': ['trousers', 'wide-leg', 'formal'], 'is_featured': True},
    {'name': 'Silk Blouse', 'brand': 'Massimo Dutti', 'category': 'Women', 'price': 599, 'original_price': 799,
     'description': 'Luxurious 100% silk blouse with a relaxed fit. Effortlessly elegant.',
     'sizes': ['XS', 'S', 'M', 'L'], 'colors': ['Ivory', 'Blush', 'Black'], 'stock': 15,
     'images': ['https://images.unsplash.com/photo-1562157873-818bc0726f68?w=600'],
     'tags': ['blouse', 'silk', 'luxury'], 'is_featured': True},
    {'name': 'Knit Cardigan', 'brand': 'Uniqlo', 'category': 'Women', 'price': 299, 'original_price': 349,
     'description': 'Cozy open-front cardigan in soft ribbed knit. Layer it over anything.',
     'sizes': ['XS', 'S', 'M', 'L', 'XL'], 'colors': ['Oatmeal', 'Dusty Pink', 'Sage'], 'stock': 40,
     'images': ['https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?w=600'],
     'tags': ['cardigan', 'knit', 'casual'], 'is_featured': False},
    {'name': 'Wrap Mini Skirt', 'brand': 'Zara', 'category': 'Women', 'price': 199, 'original_price': 249,
     'description': 'Feminine wrap mini skirt in flowing fabric. Adjustable tie waist.',
     'sizes': ['XS', 'S', 'M', 'L'], 'colors': ['Brown', 'Forest Green', 'Rust'], 'stock': 22,
     'images': ['https://images.unsplash.com/photo-1583496661160-fb5218ees96?w=600'],
     'tags': ['skirt', 'wrap', 'mini'], 'is_featured': False},

    # Accessories
    {'name': 'Leather Tote Bag', 'brand': 'Coach', 'category': 'Accessories', 'price': 999, 'original_price': 1299,
     'description': 'Premium genuine leather tote with interior zip pocket and gold hardware.',
     'sizes': ['One Size'], 'colors': ['Tan', 'Black', 'Burgundy'], 'stock': 18,
     'images': ['https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600'],
     'tags': ['bag', 'leather', 'tote', 'luxury'], 'is_featured': True},
    {'name': 'Classic Aviator Sunglasses', 'brand': 'Ray-Ban', 'category': 'Accessories', 'price': 649, 'original_price': 799,
     'description': 'Iconic aviator sunglasses with UV400 protection and gold-tone metal frame.',
     'sizes': ['One Size'], 'colors': ['Gold/Green', 'Silver/Blue'], 'stock': 30,
     'images': ['https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600'],
     'tags': ['sunglasses', 'aviator', 'classic'], 'is_featured': True},
    {'name': 'Silk Scarf', 'brand': 'Hermès Style', 'category': 'Accessories', 'price': 299, 'original_price': 299,
     'description': 'Elegant printed silk scarf. Wear as a neck scarf, headband, or bag charm.',
     'sizes': ['One Size'], 'colors': ['Multicolor', 'Blue', 'Red'], 'stock': 25,
     'images': ['https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600'],
     'tags': ['scarf', 'silk', 'accessory'], 'is_featured': False},
    {'name': 'Minimalist Watch', 'brand': 'Daniel Wellington', 'category': 'Accessories', 'price': 799, 'original_price': 999,
     'description': 'Clean-dial minimalist watch with genuine leather strap. Timeless design.',
     'sizes': ['One Size'], 'colors': ['Rose Gold', 'Silver', 'Gold'], 'stock': 20,
     'images': ['https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600'],
     'tags': ['watch', 'minimalist', 'luxury'], 'is_featured': True},
    {'name': 'Leather Belt', 'brand': 'Tommy Hilfiger', 'category': 'Accessories', 'price': 149, 'original_price': 199,
     'description': 'Classic full-grain leather belt with antique brass buckle.',
     'sizes': ['S', 'M', 'L', 'XL'], 'colors': ['Black', 'Brown', 'Tan'], 'stock': 50,
     'images': ['https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=600'],
     'tags': ['belt', 'leather', 'formal'], 'is_featured': False},

    # Sale
    {'name': 'Oversized Graphic Tee', 'brand': 'H&M', 'category': 'Sale', 'price': 49, 'original_price': 149,
     'description': 'Relaxed-fit graphic tee in heavyweight cotton. Street-style ready.',
     'sizes': ['S', 'M', 'L', 'XL', 'XXL'], 'colors': ['White', 'Black', 'Grey'], 'stock': 100,
     'images': ['https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600'],
     'tags': ['tshirt', 'graphic', 'oversized', 'sale'], 'is_featured': False},
    {'name': 'Linen Shorts', 'brand': 'Zara', 'category': 'Sale', 'price': 79, 'original_price': 199,
     'description': 'Breathable linen shorts with an elastic waistband. Summer essential.',
     'sizes': ['XS', 'S', 'M', 'L', 'XL'], 'colors': ['Ecru', 'Olive', 'Navy'], 'stock': 60,
     'images': ['https://images.unsplash.com/photo-1591195853828-11db59a44f43?w=600'],
     'tags': ['shorts', 'linen', 'summer', 'sale'], 'is_featured': False},
]

REVIEW_COMMENTS = [
    "Absolutely love this! The quality is outstanding.",
    "Great fit and the material feels premium. Will buy again.",
    "Exactly as described. Fast shipping too!",
    "Beautiful piece. Got so many compliments.",
    "Good value for money. Slightly runs large, order one size down.",
    "Perfect for the office. Very comfortable all day.",
    "The color is even more beautiful in person.",
    "High quality and the sizing is accurate.",
]


def seed():
    db_instance.connect(MONGO_URI)
    db = db_instance.db

    print("🗑  Clearing existing data...")
    db.users.drop()
    db.products.drop()
    db.orders.drop()
    db.reviews.drop()
    db.cart.drop()
    db.wishlist.drop()

    print("👤 Creating users...")
    admin = User.create('admin@ksahfashion.com', 'Admin User', 'admin123', role='admin')
    seller1 = User.create('seller@ksahfashion.com', 'Style Hub', 'seller123', role='seller',
                          phone='+601112345678')
    seller2 = User.create('trendy@ksahfashion.com', 'Trendy Picks', 'seller123', role='seller',
                          phone='+601198765432')
    customer1 = User.create('customer@ksahfashion.com', 'Sarah Johnson', 'customer123', role='customer',
                            phone='+601133445566',
                            address={'street': '12 Jalan Bukit Bintang', 'city': 'Kuala Lumpur',
                                     'state': 'WP', 'zip': '50200', 'country': 'Malaysia'})
    customer2 = User.create('jane@example.com', 'Jane Doe', 'password123', role='customer',
                            phone='+601177889900')

    print("👗 Creating products...")
    sellers = [seller1, seller2]
    product_ids = []
    for i, p_data in enumerate(PRODUCTS_DATA):
        seller = sellers[i % 2]
        product = Product({
            **p_data,
            'seller_id': seller._id,
            'seller_name': seller.name,
            'rating': round(random.uniform(3.8, 5.0), 1),
            'review_count': random.randint(5, 120),
            'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 90)),
        })
        pid = product.save()
        product_ids.append(pid)

    print("⭐ Creating reviews...")
    products = [Product.find_by_id(pid) for pid in product_ids]
    for product in products[:10]:
        for _ in range(random.randint(3, 8)):
            review = Review({
                'product_id': product._id,
                'user_id': customer1._id,
                'user_name': random.choice(['Sarah J.', 'Emma L.', 'Michael T.', 'Priya K.']),
                'rating': random.randint(4, 5),
                'title': random.choice(['Great product!', 'Love it!', 'Highly recommend', 'Perfect fit']),
                'comment': random.choice(REVIEW_COMMENTS),
                'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            })
            review.save()

    print("📦 Creating sample orders...")
    sample_products = products[:3]
    for i in range(5):
        items = []
        subtotal = 0
        for p in random.sample(sample_products, random.randint(1, 2)):
            qty = random.randint(1, 2)
            items.append({
                'product_id': p._id,
                'name': p.name,
                'brand': p.brand,
                'price': p.price,
                'size': random.choice(p.sizes),
                'color': p.colors[0] if p.colors else '',
                'quantity': qty,
                'image': p.primary_image,
            })
            subtotal += p.price * qty

        order_data = {
            'user_id': customer1._id,
            'user_name': customer1.name,
            'user_email': customer1.email,
            'items': items,
            'subtotal': subtotal,
            'discount': 0,
            'shipping_fee': 0 if subtotal >= 500 else 50,
            'total': subtotal + (0 if subtotal >= 500 else 50),
            'promo_code': '',
            'status': random.choice(['confirmed', 'processing', 'shipped', 'delivered']),
            'shipping_address': {
                'full_name': customer1.name,
                'address': '12 Jalan Bukit Bintang',
                'city': 'Kuala Lumpur',
                'state': 'WP',
                'zip_code': '50200',
                'country': 'Malaysia',
                'phone': customer1.phone,
            },
            'payment': {'method': 'card', 'status': 'completed', 'card_last4': '4242'},
            'tracking_id': f"TRK{random.randint(100000, 999999)}",
            'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 30)),
        }
        order = Order(order_data)
        order.save()

    print("\n✅ Seed complete!")
    print("─" * 40)
    print("Admin:    admin@ksahfashion.com    / admin123")
    print("Seller:   seller@ksahfashion.com   / seller123")
    print("Customer: customer@ksahfashion.com / customer123")
    print("─" * 40)


if __name__ == '__main__':
    seed()
