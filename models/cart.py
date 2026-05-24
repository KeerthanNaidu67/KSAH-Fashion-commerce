# models/cart.py
# Shopping cart model for the KSAH Fashion E-Commerce platform.
# Each customer has one Cart document in MongoDB (keyed by user_id).
# CartItem represents a single product line in the cart with size, color,
# quantity, and price. Cart supports add, update, remove, clear, and promo
# code application. get_or_create() ensures a cart always exists for a user.

from datetime import datetime
from bson import ObjectId
from database.db import get_db


class CartItem:
    def __init__(self, data: dict):
        self.product_id = data.get('product_id')
        self.seller_id = data.get('seller_id')
        self.name = data.get('name', '')
        self.price = float(data.get('price', 0))
        self.image = data.get('image', '')
        self.size = data.get('size', '')
        self.color = data.get('color', '')
        self.quantity = int(data.get('quantity', 1))
        self.brand = data.get('brand', '')

    @property
    def subtotal(self) -> float:
        return round(self.price * self.quantity, 2)

    def to_dict(self) -> dict:
        return {
            'product_id': self.product_id,
            'seller_id': self.seller_id,
            'name': self.name,
            'price': self.price,
            'image': self.image,
            'size': self.size,
            'color': self.color,
            'quantity': self.quantity,
            'brand': self.brand,
        }


class Cart:
    """Shopping cart — one per user, stored in MongoDB."""

    def __init__(self, data: dict):
        self._id = data.get('_id')
        self.user_id = data.get('user_id')
        self.items: list[CartItem] = [CartItem(i) for i in data.get('items', [])]
        self.promo_code = data.get('promo_code', '')
        self.discount = float(data.get('discount', 0))
        self.updated_at = data.get('updated_at', datetime.utcnow())

    @property
    def total(self) -> float:
        return round(sum(item.subtotal for item in self.items), 2)

    @property
    def discounted_total(self) -> float:
        return round(self.total * (1 - self.discount / 100), 2)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def add_item(self, product, size: str, color: str = '', quantity: int = 1):
        pid = str(product._id)
        for item in self.items:
            if str(item.product_id) == pid and item.size == size:
                item.quantity += quantity
                self._save()
                return
        self.items.append(CartItem({
            'product_id': product._id,
            'seller_id': product.seller_id,
            'name': product.name,
            'price': product.price,
            'image': product.primary_image,
            'size': size,
            'color': color,
            'quantity': quantity,
            'brand': product.brand,
        }))
        self._save()

    def update_item(self, product_id: str, size: str, quantity: int):
        for item in self.items:
            if str(item.product_id) == product_id and item.size == size:
                item.quantity = max(1, quantity)
                break
        self._save()

    def remove_item(self, product_id: str, size: str):
        self.items = [i for i in self.items
                      if not (str(i.product_id) == product_id and i.size == size)]
        self._save()

    def clear(self):
        self.items = []
        self.promo_code = ''
        self.discount = 0
        self._save()

    def apply_promo(self, code: str) -> bool:
        # Valid promo codes and their discount percentages
        PROMOS = {'FASHION20': 20, 'STYLE10': 10, 'NEW15': 15}
        discount = PROMOS.get(code.upper())
        if discount:
            self.promo_code = code.upper()
            self.discount = discount
            self._save()
            return True
        return False

    def _save(self):
        self.updated_at = datetime.utcnow()
        get_db().cart.update_one(
            {'user_id': self.user_id},
            {'$set': {
                'items': [i.to_dict() for i in self.items],
                'promo_code': self.promo_code,
                'discount': self.discount,
                'updated_at': self.updated_at,
            }},
            upsert=True,
        )

    @classmethod
    def get_or_create(cls, user_id) -> 'Cart':
        doc = get_db().cart.find_one({'user_id': user_id})
        if doc:
            return cls(doc)
        cart = cls({'user_id': user_id})
        get_db().cart.insert_one({'user_id': user_id, 'items': [], 'promo_code': '', 'discount': 0})
        return cart
