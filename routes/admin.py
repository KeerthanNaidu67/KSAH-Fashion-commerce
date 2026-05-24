# routes/admin.py
# Admin routes for the KSAH Fashion E-Commerce platform.
# Defines the 'admin' blueprint with prefix /admin.
# admin_required decorator enforces that only users with role='admin'
# can access these routes. Covers: dashboard, user list, toggle user status,
# product list, toggle product status, order list, and update order status.
# All business logic is delegated to AdminController.

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from functools import wraps
from controllers.admin_controller import AdminController
from models.order import ORDER_STATUSES

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('customer.home'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = AdminController.get_dashboard_stats()
    return render_template('admin/dashboard.html', **stats)


@admin_bp.route('/users')
@admin_required
def users():
    role = request.args.get('role')
    page = int(request.args.get('page', 1))
    users, total = AdminController.get_users(role, page)
    return render_template('admin/users.html', users=users, total=total,
                           page=page, role=role)


@admin_bp.route('/users/<user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    success, msg = AdminController.toggle_user_status(user_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('admin.users'))


@admin_bp.route('/products')
@admin_required
def products():
    page = int(request.args.get('page', 1))
    products, total = AdminController.get_all_products(page)
    return render_template('admin/products.html', products=products,
                           total=total, page=page)


@admin_bp.route('/products/<product_id>/toggle', methods=['POST'])
@admin_required
def toggle_product(product_id):
    success, msg = AdminController.toggle_product_status(product_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('admin.products'))


@admin_bp.route('/orders')
@admin_required
def orders():
    status_filter = request.args.get('status')
    page = int(request.args.get('page', 1))
    query = {'status': status_filter} if status_filter else {}
    order_list, total = AdminController.get_all_orders(query, page) if hasattr(AdminController, 'get_all_orders') else ([], 0)
    from models.order import Order
    order_list, total = Order.get_all(query, page)
    return render_template('admin/orders.html', orders=order_list, total=total,
                           page=page, statuses=ORDER_STATUSES, status_filter=status_filter)


@admin_bp.route('/orders/<order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    success, msg = AdminController.update_order_status(
        order_id, request.form.get('status', '')
    )
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('admin.orders'))
