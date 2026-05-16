from models.order import Order
from models.cart import Cart
from models.product import Product


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
        required = ['address', 'city', 'zip_code']
        for field in required:
            if not shipping_address.get(field):
                return False, f'{field.replace("_", " ").title()} is required.', None

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
