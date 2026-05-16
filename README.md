# KSAH — Fashion E-Commerce Platform

A full-stack fashion e-commerce web application built with Python Flask, MongoDB, and Bootstrap 5, following the MVC architectural pattern. The platform supports three user roles — Customer, Seller, and Admin — each with dedicated dashboards and access controls.

> ICT602 Software Engineering — Group Project 3

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python Flask |
| Architecture | MVC (Model-View-Controller) |
| Database | MongoDB (PyMongo) |
| Templating | Jinja2 |
| Frontend | Bootstrap 5, HTML5, CSS3, JavaScript |
| Authentication | Flask-Login + Werkzeug |
| Configuration | python-dotenv |

---

## Features

### Customer
- Browse products by category (Men, Women, Accessories)
- Search and filter by keyword, price range, size, and brand
- Shopping cart with promo code discounts
- Checkout with card, e-wallet, and COD payment options
- Order history and order tracking
- Wishlist management
- Product reviews and star ratings

### Seller
- Seller dashboard with sales statistics
- Add, edit, and delete product listings
- Product image upload
- Order management

### Admin
- Admin dashboard with platform-wide statistics
- User management (activate / suspend accounts)
- Product moderation
- Order status management

---

## Quick Start

### Prerequisites
- Python 3.10+
- MongoDB running locally on `mongodb://localhost:27017`

**Start MongoDB (macOS):**
```bash
brew services start mongodb-community
```

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd fashion-ecommerce
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed the Database
```bash
python database/seed.py
```

### 5. Run the App
```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Demo Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@ksahfashion.com | admin123 |
| Seller | seller@ksahfashion.com | seller123 |
| Customer | customer@ksahfashion.com | customer123 |

---

## Promo Codes

| Code | Discount |
|---|---|
| `FASHION20` | 20% off |
| `STYLE10` | 10% off |
| `NEW15` | 15% off |

---

## Project Structure

```
fashion-ecommerce/
├── app.py                    # Flask application entry point
├── config.py                 # DevelopmentConfig / ProductionConfig
├── requirements.txt
│
├── database/
│   ├── db.py                 # get_db() — singleton MongoDB connection
│   └── seed.py               # Demo data seeder
│
├── models/                   # Model layer (M in MVC)
│   ├── user.py               # User, Customer, Seller, Admin
│   ├── product.py            # Product, Inventory
│   ├── cart.py               # Cart, CartItem
│   ├── order.py              # Order, OrderItem
│   ├── review.py             # Product reviews
│   └── wishlist.py           # Customer wishlist
│
├── controllers/              # Controller layer (C in MVC)
│   ├── auth_controller.py
│   ├── product_controller.py
│   ├── cart_controller.py
│   ├── order_controller.py
│   ├── seller_controller.py
│   └── admin_controller.py
│
├── routes/                   # Flask Blueprints — URL mapping
│   ├── auth.py               # /login, /register, /logout
│   ├── customer.py           # /, /products, /cart, /checkout, /orders
│   ├── seller.py             # /seller/...
│   └── admin.py              # /admin/...
│
├── templates/                # View layer — Jinja2 HTML (V in MVC)
│   ├── base.html             # Shared layout
│   ├── auth/                 # login.html, register.html
│   ├── customer/             # home, products, cart, checkout, orders, wishlist
│   ├── seller/               # dashboard, products, add/edit product, orders
│   ├── admin/                # dashboard, users, products, orders
│   └── errors/               # 404.html, 500.html
│
└── static/
    ├── css/                  # Stylesheet
    ├── js/                   # Frontend JavaScript
    └── images/products/      # Uploaded product images
```

---

## Database Collections

| Collection | Purpose |
|---|---|
| `users` | All user accounts (customer / seller / admin) |
| `products` | Product catalogue managed by sellers |
| `carts` | Active shopping carts (one per user) |
| `orders` | Placed orders with status tracking |
| `reviews` | Product reviews and star ratings |
| `wishlists` | Customer saved products |
| `inventory` | Product stock management |

---

## Architecture

The application follows the **MVC (Model-View-Controller)** pattern combined with a **Client-Server** architecture:

- **Model** — `models/` handles all data, business logic, and MongoDB operations
- **View** — `templates/` renders HTML via Jinja2, no business logic
- **Controller** — `controllers/` orchestrates between Model and View
- **Routes** — `routes/` maps URLs to controller functions via Flask Blueprints
