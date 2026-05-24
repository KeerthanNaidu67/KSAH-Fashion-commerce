# app.py
# Flask application factory for the KSAH Fashion E-Commerce platform.
# Initialises the Flask app, connects to MongoDB, sets up Flask-Login,
# registers all blueprints (auth, customer, seller, admin), and attaches
# global error handlers and context processors.

import os
from flask import Flask, render_template
from flask_login import LoginManager
from config import config
from database.db import db_instance
from models.user import User

login_manager = LoginManager()


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Connect to MongoDB using the URI from config
    mongo_uri = app.config['MONGO_URI']
    db_name = mongo_uri.split('/')[-1].split('?')[0]
    db_instance.connect(mongo_uri, db_name)

    # Configure Flask-Login for session-based authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'          # redirect unauthenticated users here
    login_manager.login_message = 'Please log in to continue.'
    login_manager.login_message_category = 'warning'

    # Register blueprints for each role/module
    from routes.auth import auth_bp
    from routes.customer import customer_bp
    from routes.seller import seller_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)       # /auth/login, /auth/register, /auth/logout
    app.register_blueprint(customer_bp)   # /, /products, /cart, /checkout, /orders
    app.register_blueprint(seller_bp)     # /seller/dashboard, /seller/products, etc.
    app.register_blueprint(admin_bp)      # /admin/dashboard, /admin/users, etc.

    # Custom error pages for 404 and 500 responses
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Inject cart_count into every template so the nav badge stays updated
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        cart_count = 0
        if current_user.is_authenticated and current_user.role == 'customer':
            from models.cart import Cart
            cart = Cart.get_or_create(current_user._id)
            cart_count = cart.item_count
        return {'cart_count': cart_count}

    return app


@login_manager.user_loader
def load_user(user_id: str):
    return User.find_by_id(user_id)


if __name__ == '__main__':
    app = create_app('development')
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
