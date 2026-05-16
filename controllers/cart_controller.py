from models.cart import Cart
from models.product import Product
from models.wishlist import Wishlist


class CartController:
    """Manages cart operations."""

    @staticmethod
    def get_cart(user_id) -> Cart:
        return Cart.get_or_create(user_id)

    @staticmethod
    def add_to_cart(user_id, form_data: dict) -> tuple[bool, str]:
        product_id = form_data.get('product_id')
        size = form_data.get('size', '')
        color = form_data.get('color', '')
        quantity = int(form_data.get('quantity', 1))

        product = Product.find_by_id(product_id)
        if not product:
            return False, 'Product not found.'
        if not product.in_stock:
            return False, 'Product is out of stock.'
        if not size and product.sizes:
            return False, 'Please select a size.'

        cart = Cart.get_or_create(user_id)
        cart.add_item(product, size, color, quantity)
        return True, f'{product.name} added to cart!'

    @staticmethod
    def update_quantity(user_id, product_id: str, size: str, quantity: int) -> tuple[bool, str]:
        if quantity < 1:
            return False, 'Quantity must be at least 1.'
        cart = Cart.get_or_create(user_id)
        cart.update_item(product_id, size, quantity)
        return True, 'Cart updated.'

    @staticmethod
    def remove_item(user_id, product_id: str, size: str) -> tuple[bool, str]:
        cart = Cart.get_or_create(user_id)
        cart.remove_item(product_id, size)
        return True, 'Item removed from cart.'

    @staticmethod
    def apply_promo(user_id, code: str) -> tuple[bool, str]:
        cart = Cart.get_or_create(user_id)
        if cart.apply_promo(code):
            return True, f'Promo code "{code}" applied! {int(cart.discount)}% off.'
        return False, 'Invalid promo code.'

    @staticmethod
    def toggle_wishlist(user_id, product_id: str) -> tuple[bool, str]:
        wl = Wishlist.get_or_create(user_id)
        if wl.contains(product_id):
            wl.remove(product_id)
            return False, 'Removed from wishlist.'
        wl.add(product_id)
        return True, 'Added to wishlist.'
