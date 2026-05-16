from models.user import User
from models.product import Product
from models.order import Order
from database.db import get_db


class AdminController:
    """Platform-wide administration."""

    @staticmethod
    def get_dashboard_stats() -> dict:
        db = get_db()
        total_users = db.users.count_documents({'role': 'customer'})
        total_sellers = db.users.count_documents({'role': 'seller'})
        total_products = db.products.count_documents({'is_active': True})
        total_orders = db.orders.count_documents({})
        revenue_stats = Order.get_revenue_stats()
        pending_orders = db.orders.count_documents({'status': 'pending'})

        # Monthly revenue pipeline
        pipeline = [
            {'$match': {'status': 'delivered'}},
            {'$group': {
                '_id': {
                    'year': {'$year': '$created_at'},
                    'month': {'$month': '$created_at'},
                },
                'revenue': {'$sum': '$total'},
                'orders': {'$count': {}},
            }},
            {'$sort': {'_id.year': 1, '_id.month': 1}},
            {'$limit': 12},
        ]
        monthly = list(db.orders.aggregate(pipeline))

        return {
            'total_users': total_users,
            'total_sellers': total_sellers,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': revenue_stats.get('total_revenue', 0),
            'avg_order': revenue_stats.get('avg_order', 0),
            'pending_orders': pending_orders,
            'monthly_data': monthly,
            'recent_orders': Order.get_all(page=1, per_page=5)[0],
        }

    @staticmethod
    def get_users(role: str = None, page: int = 1, per_page: int = 20) -> tuple:
        query = {}
        if role:
            query['role'] = role
        db = get_db()
        total = db.users.count_documents(query)
        skip = (page - 1) * per_page
        docs = db.users.find(query).sort('created_at', -1).skip(skip).limit(per_page)
        users = [User(d) for d in docs]
        return users, total

    @staticmethod
    def toggle_user_status(user_id: str) -> tuple[bool, str]:
        user = User.find_by_id(user_id)
        if not user:
            return False, 'User not found.'
        if user.role == 'admin':
            return False, 'Cannot modify admin accounts.'
        user.update_status(not user.is_active)
        status = 'activated' if user.is_active else 'suspended'
        return True, f'User {status} successfully.'

    @staticmethod
    def get_all_products(page: int = 1, per_page: int = 20) -> tuple:
        db = get_db()
        total = db.products.count_documents({})
        skip = (page - 1) * per_page
        docs = db.products.find({}).sort('created_at', -1).skip(skip).limit(per_page)
        products = [Product(d) for d in docs]
        return products, total

    @staticmethod
    def toggle_product_status(product_id: str) -> tuple[bool, str]:
        product = Product.find_by_id(product_id)
        if not product:
            return False, 'Product not found.'
        product.is_active = not product.is_active
        product.save()
        status = 'activated' if product.is_active else 'deactivated'
        return True, f'Product {status}.'

    @staticmethod
    def update_order_status(order_id: str, status: str) -> tuple[bool, str]:
        order = Order.find_by_id(order_id)
        if not order:
            return False, 'Order not found.'
        try:
            order.update_status(status)
            return True, f'Order status updated to {status}.'
        except ValueError as e:
            return False, str(e)
