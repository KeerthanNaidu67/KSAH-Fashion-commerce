# controllers/auth_controller.py
# Authentication controller for the KSAH Fashion E-Commerce platform.
# Handles user registration with field validation, login with password
# checking and account status verification, and logout.
# Used by routes/auth.py. Returns (bool, message) tuples so the route
# layer can flash the message and redirect accordingly.

from flask import flash
from models.user import User
from flask_login import login_user, logout_user


class AuthController:
    """Handles registration, login, logout logic."""

    @staticmethod
    def register(form_data: dict) -> tuple[bool, str]:
        email = form_data.get('email', '').lower().strip()
        name = form_data.get('name', '').strip()
        password = form_data.get('password', '')
        confirm = form_data.get('confirm_password', '')
        role = form_data.get('role', 'customer')

        if not all([email, name, password]):
            return False, 'All fields are required.'
        if len(password) < 6:
            return False, 'Password must be at least 6 characters.'
        if password != confirm:
            return False, 'Passwords do not match.'
        if role not in User.ROLES:
            return False, 'Invalid role.'
        if User.find_by_email(email):
            return False, 'An account with this email already exists.'

        user = User.create(
            email=email,
            name=name,
            password=password,
            role=role,
            phone=form_data.get('phone', ''),
        )
        login_user(user, remember=True)
        return True, f'Welcome, {name}! Your account has been created.'

    @staticmethod
    def login(email: str, password: str, remember: bool = False) -> tuple[bool, str]:
        user = User.find_by_email(email)
        if not user:
            return False, 'No account found with that email.'
        if not user.check_password(password):
            return False, 'Incorrect password.'
        if not user.is_active:
            return False, 'Your account has been suspended. Contact support.'
        login_user(user, remember=remember)
        return True, f'Welcome back, {user.name}!'

    @staticmethod
    def logout():
        logout_user()
