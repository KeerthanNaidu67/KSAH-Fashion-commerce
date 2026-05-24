# routes/customer.py
# Customer-facing routes for the KSAH Fashion E-Commerce platform.
# Defines the 'customer' blueprint (no URL prefix — serves the root domain).
# Covers: home, product listing, product detail, cart CRUD, promo codes,
# checkout, order confirmation, order history, order tracking, wishlist,
# review submission, search, and contact page.
# Cart/wishlist endpoints support both JSON (AJAX) and form-POST responses.

from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify)
from flask_login import login_required, current_user
from controllers.product_controller import ProductController
from controllers.cart_controller import CartController
from controllers.order_controller import OrderController
from models.wishlist import Wishlist
from models.product import CATEGORIES, SIZES

customer_bp = Blueprint('customer', __name__)


def _customer_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated and current_user.role not in ('customer',):
            flash('Access restricted.', 'warning')
            return redirect(url_for('customer.home'))
        return f(*args, **kwargs)
    return decorated


@customer_bp.route('/')
def home():
    data = ProductController.get_home_data()
    return render_template('customer/home.html', **data, categories=CATEGORIES)


@customer_bp.route('/products')
def products():
    data = ProductController.get_product_list(request.args)
    return render_template('customer/products.html', **data,
                           categories=CATEGORIES, sizes=SIZES)


@customer_bp.route('/products/<product_id>')
def product_detail(product_id):
    data = ProductController.get_product_detail(product_id)
    if not data:
        flash('Product not found.', 'error')
        return redirect(url_for('customer.products'))
    in_wishlist = False
    if current_user.is_authenticated:
        wl = Wishlist.get_or_create(current_user._id)
        in_wishlist = wl.contains(product_id)
    return render_template('customer/product_detail.html', **data,
                           in_wishlist=in_wishlist, sizes=SIZES)


# ── Cart ───────────────────────────────────────────────────────────

@customer_bp.route('/cart')
@login_required
def cart():
    cart = CartController.get_cart(current_user._id)
    return render_template('customer/cart.html', cart=cart)


@customer_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    success, msg = CartController.add_to_cart(current_user._id, request.form)
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = CartController.get_cart(current_user._id)
        return jsonify({'success': success, 'message': msg, 'count': cart.item_count})
    flash(msg, 'success' if success else 'error')
    return redirect(request.referrer or url_for('customer.cart'))


@customer_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    success, msg = CartController.update_quantity(
        current_user._id,
        request.form.get('product_id'),
        request.form.get('size', ''),
        int(request.form.get('quantity', 1)),
    )
    if request.is_json:
        cart = CartController.get_cart(current_user._id)
        return jsonify({'success': success, 'total': cart.discounted_total, 'count': cart.item_count})
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('customer.cart'))


@customer_bp.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    CartController.remove_item(
        current_user._id,
        request.form.get('product_id'),
        request.form.get('size', ''),
    )
    if request.is_json:
        cart = CartController.get_cart(current_user._id)
        return jsonify({'success': True, 'count': cart.item_count, 'total': cart.discounted_total})
    flash('Item removed.', 'info')
    return redirect(url_for('customer.cart'))


@customer_bp.route('/cart/promo', methods=['POST'])
@login_required
def apply_promo():
    success, msg = CartController.apply_promo(current_user._id, request.form.get('code', ''))
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('customer.cart'))


# ── Checkout ───────────────────────────────────────────────────────

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = CartController.get_cart(current_user._id)
    if not cart.items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('customer.cart'))
    if request.method == 'POST':
        success, msg, order_id = OrderController.checkout(current_user, request.form)
        if success:
            flash(msg, 'success')
            return redirect(url_for('customer.order_confirmation', order_id=order_id))
        flash(msg, 'error')
    return render_template('customer/checkout.html', cart=cart, user=current_user)


@customer_bp.route('/order/confirmation/<order_id>')
@login_required
def order_confirmation(order_id):
    order = OrderController.get_order_detail(order_id, current_user._id)
    if not order:
        return redirect(url_for('customer.home'))
    return render_template('customer/order_confirmation.html', order=order)


@customer_bp.route('/orders')
@login_required
def orders():
    user_orders = OrderController.get_user_orders(current_user._id)
    return render_template('customer/orders.html', orders=user_orders)


@customer_bp.route('/orders/<order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    success, msg = OrderController.cancel_order(order_id, current_user._id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('customer.orders'))


@customer_bp.route('/orders/<order_id>/track')
@login_required
def track_order(order_id):
    order = OrderController.get_order_detail(order_id, current_user._id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('customer.orders'))
    return render_template('customer/order_tracking.html', order=order)


# ── Wishlist ───────────────────────────────────────────────────────

@customer_bp.route('/wishlist')
@login_required
def wishlist():
    wl = Wishlist.get_or_create(current_user._id)
    products = wl.get_products()
    return render_template('customer/wishlist.html', products=products)


@customer_bp.route('/wishlist/toggle', methods=['POST'])
@login_required
def toggle_wishlist():
    product_id = request.form.get('product_id')
    added, msg = CartController.toggle_wishlist(current_user._id, product_id)
    if request.is_json:
        return jsonify({'success': True, 'added': added, 'message': msg})
    flash(msg, 'info')
    return redirect(request.referrer or url_for('customer.wishlist'))


# ── Reviews ────────────────────────────────────────────────────────

@customer_bp.route('/products/<product_id>/review', methods=['POST'])
@login_required
def submit_review(product_id):
    success, msg = ProductController.submit_review(product_id, current_user, request.form)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('customer.product_detail', product_id=product_id))


# ── Search ─────────────────────────────────────────────────────────

@customer_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('customer.products'))
    return redirect(url_for('customer.products', q=q))


@customer_bp.route('/api/search-suggestions')
def search_suggestions():
    from models.product import Product
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])
    results = Product.search(q, limit=6)
    return jsonify([{'name': p.name, 'id': str(p._id), 'brand': p.brand} for p in results])


@customer_bp.route('/contact')
def contact():
    return render_template('customer/contact.html')

