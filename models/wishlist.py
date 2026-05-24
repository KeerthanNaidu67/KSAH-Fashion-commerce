# models/wishlist.py
# Wishlist model for the KSAH Fashion E-Commerce platform.
# Each customer has one Wishlist document storing a list of product ObjectIds.
# Supports add, remove, contains check, and get_products() to load full
# Product objects. get_or_create() ensures a wishlist always exists for a user.

from bson import ObjectId
from database.db import get_db


class Wishlist:
    """Customer wishlist — stores product references."""

    def __init__(self, data: dict):
        self._id = data.get('_id')
        self.user_id = data.get('user_id')
        self.product_ids: list = data.get('product_ids', [])

    def add(self, product_id):
        pid = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        if pid not in self.product_ids:
            self.product_ids.append(pid)
            self._save()

    def remove(self, product_id):
        pid = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        self.product_ids = [p for p in self.product_ids if p != pid]
        self._save()

    def contains(self, product_id) -> bool:
        try:
            pid = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
            return pid in self.product_ids
        except Exception:
            return False

    def get_products(self) -> list:
        from models.product import Product
        return [Product.find_by_id(str(pid)) for pid in self.product_ids
                if Product.find_by_id(str(pid))]

    def _save(self):
        get_db().wishlist.update_one(
            {'user_id': self.user_id},
            {'$set': {'product_ids': self.product_ids}},
            upsert=True,
        )

    @classmethod
    def get_or_create(cls, user_id) -> 'Wishlist':
        doc = get_db().wishlist.find_one({'user_id': user_id})
        if doc:
            return cls(doc)
        return cls({'user_id': user_id, 'product_ids': []})
