# models/product.py
# Product model for the KSAH Fashion E-Commerce platform.
# Represents fashion products listed by sellers. Supports filtering by category,
# brand, price range, size, and keyword search via MongoDB regex queries.
# Also tracks stock levels, ratings, and featured status.
# Used by sellers (CRUD), customers (browse/search), and admins (moderation).

from datetime import datetime
from bson import ObjectId
from database.db import get_db


CATEGORIES = ['Men', 'Women', 'Kids', 'Accessories', 'Sale']
SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']


class Product:
    """Product model — managed by sellers, browsed by customers."""

    def __init__(self, data: dict):
        self._id = data.get('_id')
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.price = float(data.get('price', 0))
        self.original_price = float(data.get('original_price', 0))
        self.category = data.get('category', '')
        self.brand = data.get('brand', '')
        self.sizes = data.get('sizes', [])
        self.colors = data.get('colors', [])
        self.images = data.get('images', [])
        self.stock = int(data.get('stock', 0))
        self.seller_id = data.get('seller_id')
        self.seller_name = data.get('seller_name', '')
        self.tags = data.get('tags', [])
        self.is_active = data.get('is_active', True)
        self.is_featured = data.get('is_featured', False)
        self.rating = float(data.get('rating', 0))
        self.review_count = int(data.get('review_count', 0))
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())

    @property
    def discount_percent(self) -> int:
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0

    @property
    def primary_image(self) -> str:
        return self.images[0] if self.images else '/static/images/placeholder.jpg'

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'original_price': self.original_price,
            'category': self.category,
            'brand': self.brand,
            'sizes': self.sizes,
            'colors': self.colors,
            'images': self.images,
            'stock': self.stock,
            'seller_id': self.seller_id,
            'seller_name': self.seller_name,
            'tags': self.tags,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'rating': self.rating,
            'review_count': self.review_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    # ── DB operations ──────────────────────────────────────────────

    @classmethod
    def find_by_id(cls, product_id: str):
        try:
            doc = get_db().products.find_one({'_id': ObjectId(product_id)})
            return cls(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def get_all(cls, filters: dict = None, sort_by: str = 'created_at',
                page: int = 1, per_page: int = 12) -> tuple:
        query = {'is_active': True}
        if filters:
            if filters.get('category'):
                query['category'] = filters['category']
            if filters.get('brand'):
                query['brand'] = {'$in': filters['brand']}
            if filters.get('min_price') is not None:
                query.setdefault('price', {})['$gte'] = float(filters['min_price'])
            if filters.get('max_price') is not None:
                query.setdefault('price', {})['$lte'] = float(filters['max_price'])
            if filters.get('size'):
                query['sizes'] = {'$in': filters['size']}
            if filters.get('search'):
                query['$or'] = [
                    {'name': {'$regex': filters['search'], '$options': 'i'}},
                    {'brand': {'$regex': filters['search'], '$options': 'i'}},
                    {'tags': {'$regex': filters['search'], '$options': 'i'}},
                ]
        sort_map = {
            'price_asc': [('price', 1)],
            'price_desc': [('price', -1)],
            'rating': [('rating', -1)],
            'newest': [('created_at', -1)],
        }
        sort = sort_map.get(sort_by, [('created_at', -1)])
        col = get_db().products
        total = col.count_documents(query)
        skip = (page - 1) * per_page
        docs = col.find(query).sort(sort).skip(skip).limit(per_page)
        return [cls(d) for d in docs], total

    @classmethod
    def get_featured(cls, limit: int = 8) -> list:
        docs = get_db().products.find({'is_featured': True, 'is_active': True}).limit(limit)
        return [cls(d) for d in docs]

    @classmethod
    def get_by_seller(cls, seller_id, page: int = 1, per_page: int = 20) -> list:
        skip = (page - 1) * per_page
        docs = (get_db().products
                .find({'seller_id': seller_id})
                .sort('created_at', -1)
                .skip(skip)
                .limit(per_page))
        return [cls(d) for d in docs]

    @classmethod
    def get_by_category(cls, category: str, limit: int = 8) -> list:
        docs = get_db().products.find({'category': category, 'is_active': True}).limit(limit)
        return [cls(d) for d in docs]

    @classmethod
    def search(cls, query: str, limit: int = 20) -> list:
        docs = get_db().products.find({
            'is_active': True,
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'brand': {'$regex': query, '$options': 'i'}},
                {'category': {'$regex': query, '$options': 'i'}},
            ]
        }).limit(limit)
        return [cls(d) for d in docs]

    @classmethod
    def count_by_seller(cls, seller_id) -> int:
        return get_db().products.count_documents({'seller_id': seller_id})

    @classmethod
    def count_low_stock(cls, seller_id, threshold: int = 5) -> int:
        return get_db().products.count_documents({
            'seller_id': seller_id,
            'stock': {'$lte': threshold},
            'stock': {'$gt': 0},
        })

    def save(self) -> str:
        self.updated_at = datetime.utcnow()
        db = get_db()
        if self._id:
            db.products.update_one({'_id': self._id}, {'$set': self.to_dict()})
            return str(self._id)
        result = db.products.insert_one(self.to_dict())
        self._id = result.inserted_id
        return str(self._id)

    def delete(self):
        get_db().products.delete_one({'_id': self._id})

    def update_stock(self, delta: int):
        self.stock = max(0, self.stock + delta)
        get_db().products.update_one({'_id': self._id}, {'$set': {'stock': self.stock}})

    def update_rating(self, new_rating: float, new_count: int):
        self.rating = round(new_rating, 1)
        self.review_count = new_count
        get_db().products.update_one(
            {'_id': self._id},
            {'$set': {'rating': self.rating, 'review_count': self.review_count}}
        )
