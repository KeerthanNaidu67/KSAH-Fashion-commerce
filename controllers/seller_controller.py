# controllers/seller_controller.py
# Seller controller for the KSAH Fashion E-Commerce platform.
# Handles all seller dashboard operations: dashboard statistics (products,
# stock levels, orders, revenue), and full product CRUD with image upload.
# _allowed_file() validates uploaded image file extensions before saving.
# Each operation enforces seller ownership — sellers can only edit/delete
# their own products. Used by routes/seller.py.

import os
from datetime import datetime
from werkzeug.utils import secure_filename
from models.product import Product, CATEGORIES, SIZES
from models.order import Order
from database.db import get_db


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _allowed_file(filename: str) -> bool:
    # Check if the uploaded file has a permitted image extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class SellerController:
    """Business logic for seller dashboard."""

    @staticmethod
    def get_dashboard_stats(seller_id) -> dict:
        db = get_db()
        total_products = Product.count_by_seller(seller_id)
        low_stock_count = db.products.count_documents({
            'seller_id': seller_id,
            'stock': {'$lte': 5, '$gt': 0}
        })
        out_of_stock = db.products.count_documents({'seller_id': seller_id, 'stock': 0})

        orders = Order.get_seller_orders(seller_id)
        total_revenue = sum(
            sum(i.price * i.quantity for i in o.items if str(i.product_id) in
                [str(p._id) for p in Product.get_by_seller(seller_id, per_page=1000)])
            for o in orders
        )
        # Simplified revenue from all orders containing seller products
        total_revenue = sum(o.total for o in orders)
        return {
            'total_products': total_products,
            'low_stock': low_stock_count,
            'out_of_stock': out_of_stock,
            'total_orders': len(orders),
            'total_revenue': round(total_revenue, 2),
            'recent_orders': orders[:5],
        }

    @staticmethod
    def get_products(seller_id, page: int = 1) -> list:
        return Product.get_by_seller(seller_id, page=page)

    @staticmethod
    def add_product(seller, form_data: dict, files, upload_folder: str) -> tuple[bool, str]:
        name = form_data.get('name', '').strip()
        if not name:
            return False, 'Product name is required.'

        try:
            price = float(form_data.get('price', 0))
            original_price = float(form_data.get('original_price', price))
            stock = int(form_data.get('stock', 0))
        except ValueError:
            return False, 'Invalid price or stock value.'

        images = []
        if files and 'images' in files:
            os.makedirs(upload_folder, exist_ok=True)
            for f in files.getlist('images'):
                if f and _allowed_file(f.filename):
                    # Prefix filename with timestamp to avoid name collisions
                    fname = secure_filename(f.filename)
                    fname = f"{datetime.utcnow().timestamp()}_{fname}"
                    f.save(os.path.join(upload_folder, fname))
                    images.append(f'/static/images/products/{fname}')

        product = Product({
            'name': name,
            'description': form_data.get('description', ''),
            'price': price,
            'original_price': original_price,
            'category': form_data.get('category', ''),
            'brand': form_data.get('brand', ''),
            'sizes': form_data.getlist('sizes'),
            'colors': [c.strip() for c in form_data.get('colors', '').split(',') if c.strip()],
            'stock': stock,
            'seller_id': seller._id,
            'seller_name': seller.name,
            'images': images,
            'tags': [t.strip() for t in form_data.get('tags', '').split(',') if t.strip()],
            'is_featured': 'is_featured' in form_data,
            'created_at': datetime.utcnow(),
        })
        product.save()
        return True, f'Product "{name}" added successfully!'

    @staticmethod
    def update_product(product_id: str, seller_id, form_data: dict, files,
                       upload_folder: str) -> tuple[bool, str]:
        product = Product.find_by_id(product_id)
        if not product or product.seller_id != seller_id:
            return False, 'Product not found or unauthorized.'

        try:
            product.price = float(form_data.get('price', product.price))
            product.original_price = float(form_data.get('original_price', product.original_price))
            product.stock = int(form_data.get('stock', product.stock))
        except ValueError:
            return False, 'Invalid numeric values.'

        product.name = form_data.get('name', product.name).strip()
        product.description = form_data.get('description', product.description)
        product.category = form_data.get('category', product.category)
        product.brand = form_data.get('brand', product.brand)
        product.sizes = form_data.getlist('sizes') or product.sizes
        product.colors = [c.strip() for c in form_data.get('colors', '').split(',') if c.strip()]
        product.tags = [t.strip() for t in form_data.get('tags', '').split(',') if t.strip()]
        product.is_featured = 'is_featured' in form_data
        product.is_active = 'is_active' in form_data

        if files and 'images' in files:
            os.makedirs(upload_folder, exist_ok=True)
            for f in files.getlist('images'):
                if f and _allowed_file(f.filename):
                    fname = secure_filename(f.filename)
                    fname = f"{datetime.utcnow().timestamp()}_{fname}"
                    f.save(os.path.join(upload_folder, fname))
                    product.images.append(f'/static/images/products/{fname}')

        product.save()
        return True, 'Product updated successfully!'

    @staticmethod
    def delete_product(product_id: str, seller_id) -> tuple[bool, str]:
        product = Product.find_by_id(product_id)
        if not product or product.seller_id != seller_id:
            return False, 'Not found or unauthorized.'
        product.delete()
        return True, 'Product deleted.'
