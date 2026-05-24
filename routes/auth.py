# routes/auth.py
# Authentication routes for the KSAH Fashion E-Commerce platform.
# Defines the 'auth' blueprint with prefix /auth.
# Routes: GET/POST /auth/login, GET/POST /auth/register, GET /auth/logout.
# _redirect_by_role() maps each user role to its home dashboard URL.
# All business logic is delegated to AuthController.

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, logout_user, current_user
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)
    if request.method == 'POST':
        success, msg = AuthController.login(
            email=request.form.get('email', ''),
            password=request.form.get('password', ''),
            remember='remember' in request.form,
        )
        if success:
            flash(msg, 'success')
            next_url = request.args.get('next')
            return redirect(next_url or _redirect_by_role(current_user.role))
        flash(msg, 'error')
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    if request.method == 'POST':
        success, msg = AuthController.register(request.form)
        if success:
            flash(msg, 'success')
            return redirect(_redirect_by_role(current_user.role))
        flash(msg, 'error')
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    AuthController.logout()
    flash('You have been logged out.', 'info')
    return redirect(url_for('customer.home'))


def _redirect_by_role(role: str):
    routes = {
        'admin': url_for('admin.dashboard'),
        'seller': url_for('seller.dashboard'),
        'customer': url_for('customer.home'),
    }
    return routes.get(role, url_for('customer.home'))
