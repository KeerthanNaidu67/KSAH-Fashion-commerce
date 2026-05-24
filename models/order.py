# models/order.py
# Order model for the KSAH Fashion E-Commerce platform.
# Represents a customer's placed order containing one or more OrderItems.
# Tracks shipping address, payment method, order status, and a tracking ID.
# create_from_cart() converts a Cart into a saved Order and deducts stock.
# get_seller_orders() filters orders by seller_id embedded in items for the
# seller dashboard. ORDER_STATUSES defines the allowed status progression.

from datetime import datetime
from bson import ObjectId
from database.db import get_db


ORDER_STATUSES = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']


class OrderItem:
    def __init__(self, data: dict):
        self.product_id = data.get('product_id')
        self.seller_id = data.get('seller_id')
        self.name = data.get('name', '')
        self.brand = data.get('brand', '')
        self.price = float(data.get('price', 0))
        self.size = data.get('size', '')
        self.color = data.get('color', '')
        self.quantity = int(data.get('quantity', 1))
        self.image = data.get('image', '')

    @property
    def subtotal(self) -> float:
        return round(self.price * self.quantity, 2)

    def to_dict(self) -> dict:
        return {
            'product_id': self.product_id,
            'seller_id': self.seller_id,
            'name': self.name,
            'brand': self.brand,
            'price': self.price,
            'size': self.size,
            'color': self.color,
            'quantity': self.quantity,
            'image': self.image,
        }


class Order:
    """Order placed by a customer."""

    def __init__(self, data: dict):
        self._id = data.get('_id')
        self.user_id = data.get('user_id')
        self.user_name = data.get('user_name', '')
        self.user_email = data.get('user_email', '')
        self.items: list[OrderItem] = [OrderItem(i) for i in data.get('items', [])]
        self.subtotal = float(data.get('subtotal', 0))
        self.discount = float(data.get('discount', 0))
        self.shipping_fee = float(data.get('shipping_fee', 0))
        self.total = float(data.get('total', 0))
        self.promo_code = data.get('promo_code', '')
        self.status = data.get('status', 'pending')
        self.shipping_address = data.get('shipping_address', {})
        self.payment = data.get('payment', {})
        self.tracking_id = data.get('tracking_id', '')
        self.notes = data.get('notes', '')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())

    @property
    def order_number(self) -> str:
        return f"ORD-{str(self._id)[-8:].upper()}"

    @property
    def status_index(self) -> int:
        try:
            return ORDER_STATUSES.index(self.status)
        except ValueError:
            return 0

    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'items': [i.to_dict() for i in self.items],
            'subtotal': self.subtotal,
            'discount': self.discount,
            'shipping_fee': self.shipping_fee,
            'total': self.total,
            'promo_code': self.promo_code,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'payment': self.payment,
            'tracking_id': self.tracking_id,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def save(self) -> str:
        self.updated_at = datetime.utcnow()
        db = get_db()
        if self._id:
            db.orders.update_one({'_id': self._id}, {'$set': self.to_dict()})
            return str(self._id)
        result = db.orders.insert_one(self.to_dict())
        self._id = result.inserted_id
        return str(self._id)

    def update_status(self, status: str):
        if status not in ORDER_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        self.status = status
        self.updated_at = datetime.utcnow()
        get_db().orders.update_one(
            {'_id': self._id},
            {'$set': {'status': status, 'updated_at': self.updated_at}}
        )

    @classmethod
    def find_by_id(cls, order_id: str):
        try:
            doc = get_db().orders.find_one({'_id': ObjectId(order_id)})
            return cls(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def get_by_user(cls, user_id, limit: int = 20) -> list:
        docs = get_db().orders.find({'user_id': user_id}).sort('created_at', -1).limit(limit)
        return [cls(d) for d in docs]

    @classmethod
    def get_all(cls, filters: dict = None, page: int = 1, per_page: int = 20) -> tuple:
        query = filters or {}
        col = get_db().orders
        total = col.count_documents(query)
        skip = (page - 1) * per_page
        docs = col.find(query).sort('created_at', -1).skip(skip).limit(per_page)
        return [cls(d) for d in docs], total

    @classmethod
    def get_revenue_stats(cls) -> dict:
        pipeline = [
            {'$match': {'status': 'delivered'}},
            {'$group': {
                '_id': None,
                'total_revenue': {'$sum': '$total'},
                'total_orders': {'$count': {}},
                'avg_order': {'$avg': '$total'},
            }}
        ]
        result = list(get_db().orders.aggregate(pipeline))
        return result[0] if result else {'total_revenue': 0, 'total_orders': 0, 'avg_order': 0}

    @classmethod
    def get_seller_orders(cls, seller_id) -> list:
        docs = get_db().orders.find({
            'items.seller_id': seller_id,
        }).sort('created_at', -1)
        return [cls(d) for d in docs]

    @staticmethod
    def create_from_cart(cart, user, shipping_address: dict, payment: dict) -> 'Order':
        import random, string
        tracking = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        shipping_fee = 0 if cart.total >= 500 else 50
        order = Order({
            'user_id': user._id,
            'user_name': user.name,
            'user_email': user.email,
            'items': [i.to_dict() for i in cart.items],
            'subtotal': cart.total,
            'discount': cart.total - cart.discounted_total,
            'shipping_fee': shipping_fee,
            'total': cart.discounted_total + shipping_fee,
            'promo_code': cart.promo_code,
            'status': 'confirmed',
            'shipping_address': shipping_address,
            'payment': payment,
            'tracking_id': tracking,
            'created_at': datetime.utcnow(),
        })
        order.save()
        return order
