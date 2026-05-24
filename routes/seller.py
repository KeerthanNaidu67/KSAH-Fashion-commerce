# routes/seller.py
# Seller routes for the KSAH Fashion E-Commerce platform.
# Defines the 'seller' blueprint with prefix /seller.
# seller_required decorator enforces that only users with role='seller'
# can access these routes. Covers: dashboard, product list, add product,
# edit product, delete product, and seller order list.
# All business logic is delegated to SellerController.

from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, current_app)
from flask_login import login_required, current_user
from functools import wraps
from controllers.seller_controller import SellerController
from models.product import CATEGORIES, SIZES

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')


def seller_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'seller':
            flash('Seller access required.', 'error')
            return redirect(url_for('customer.home'))
        return f(*args, **kwargs)
    return decorated


@seller_bp.route('/dashboard')
@seller_required
def dashboard():
    stats = SellerController.get_dashboard_stats(current_user._id)
    return render_template('seller/dashboard.html', **stats)


@seller_bp.route('/products')
@seller_required
def products():
    page = int(request.args.get('page', 1))
    products = SellerController.get_products(current_user._id, page)
    return render_template('seller/products.html', products=products, page=page)


@seller_bp.route('/products/add', methods=['GET', 'POST'])
@seller_required
def add_product():
    if request.method == 'POST':
        upload_folder = current_app.config['UPLOAD_FOLDER']
        success, msg = SellerController.add_product(
            current_user, request.form, request.files, upload_folder
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('seller.products'))
    return render_template('seller/add_product.html', categories=CATEGORIES, sizes=SIZES)


@seller_bp.route('/products/<product_id>/edit', methods=['GET', 'POST'])
@seller_required
def edit_product(product_id):
    from models.product import Product
    product = Product.find_by_id(product_id)
    if not product or product.seller_id != current_user._id:
        flash('Product not found.', 'error')
        return redirect(url_for('seller.products'))
    if request.method == 'POST':
        upload_folder = current_app.config['UPLOAD_FOLDER']
        success, msg = SellerController.update_product(
            product_id, current_user._id, request.form, request.files, upload_folder
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('seller.products'))
    return render_template('seller/edit_product.html', product=product,
                           categories=CATEGORIES, sizes=SIZES)


@seller_bp.route('/products/<product_id>/delete', methods=['POST'])
@seller_required
def delete_product(product_id):
    success, msg = SellerController.delete_product(product_id, current_user._id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('seller.products'))


@seller_bp.route('/orders')
@seller_required
def orders():
    from models.order import Order
    seller_orders = Order.get_seller_orders(current_user._id)
    return render_template('seller/orders.html', orders=seller_orders)
