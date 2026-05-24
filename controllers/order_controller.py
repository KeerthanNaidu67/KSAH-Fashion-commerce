# controllers/order_controller.py
# Order controller for the KSAH Fashion E-Commerce platform.
# Handles the full checkout flow: validating cart contents, building the
# shipping address and payment dict, deducting product stock, creating
# the Order from the Cart, and clearing the cart on success.
# Also provides order history, detail view, and cancellation.
# Used by routes/customer.py.

from datetime import datetime
from models.order import Order
from models.cart import Cart
from models.product import Product
from database.db import get_db


class OrderController:
    """Handles checkout and order management."""

    @staticmethod
    def checkout(user, form_data: dict) -> tuple[bool, str, str]:
        """Process checkout → returns (success, message, order_id)."""
        cart = Cart.get_or_create(user._id)
        if not cart.items:
            return False, 'Your cart is empty.', None

        shipping_address = {
            'full_name': form_data.get('full_name', user.name),
            'address': form_data.get('address', ''),
            'city': form_data.get('city', ''),
            'state': form_data.get('state', ''),
            'zip_code': form_data.get('zip_code', ''),
            'country': form_data.get('country', 'Malaysia'),
            'phone': form_data.get('phone', ''),
        }

        payment = {
            'method': form_data.get('payment_method', 'card'),
            'status': 'completed',
            'card_last4': form_data.get('card_number', '')[-4:] if form_data.get('card_number') else '',
        }

        # Validate required fields
        required = ['full_name', 'phone', 'address', 'city', 'zip_code']
        for field in required:
            if not shipping_address.get(field) and not (field == 'full_name' and user.name):
                label = field.replace('_', ' ').title()
                return False, f'{label} is required.', None

        # Deduct stock
        for item in cart.items:
            product = Product.find_by_id(str(item.product_id))
            if product:
                product.update_stock(-item.quantity)

        order = Order.create_from_cart(cart, user, shipping_address, payment)
        cart.clear()
        return True, 'Order placed successfully!', str(order._id)

    @staticmethod
    def get_user_orders(user_id) -> list:
        return Order.get_by_user(user_id)

    @staticmethod
    def get_order_detail(order_id: str, user_id=None) -> Order:
        order = Order.find_by_id(order_id)
        if not order:
            return None
        if user_id and order.user_id != user_id:
            return None
        return order

    @staticmethod
    def cancel_order(order_id: str, user_id) -> tuple[bool, str]:
        order = Order.find_by_id(order_id)
        if not order:
            return False, 'Order not found.'
        if order.user_id != user_id:
            return False, 'Unauthorized.'
        if order.status not in ('pending', 'confirmed'):
            return False, 'Order cannot be cancelled at this stage.'
        get_db().orders.update_one(
            {'_id': order._id},
            {'$set': {'status': 'cancelled', 'updated_at': datetime.utcnow()}}
        )
        return True, 'Order cancelled successfully.'
