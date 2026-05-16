# LUXE — Fashion E-Commerce Platform
## ICT602 Group Project 3

A modern, full-stack fashion e-commerce platform built with Flask, MongoDB, and Bootstrap 5.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python Flask (MVC) |
| Database | MongoDB (PyMongo) |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Auth | Flask-Login + Werkzeug |
| Templates | Jinja2 |

---

## Quick Start

### Prerequisites
- Python 3.10+
- MongoDB running locally (`mongodb://localhost:27017`)

### 1. Install Dependencies
```bash
cd fashion-ecommerce
pip install -r requirements.txt
```

### 2. Seed the Database
```bash
python database/seed.py
```

### 3. Run the App
```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@luxefashion.com | admin123 |
| Seller | seller@luxefashion.com | seller123 |
| Customer | customer@luxefashion.com | customer123 |

---

## Project Structure

```
fashion-ecommerce/
├── app.py                    # Flask application factory
├── config.py                 # Environment configuration
├── requirements.txt
│
├── database/
│   ├── db.py                 # MongoDB singleton connector
│   └── seed.py               # Sample data seeder
│
├── models/                   # Data layer (M in MVC)
│   ├── user.py               # User, Customer, Seller, Admin
│   ├── product.py            # Product model
│   ├── cart.py               # Cart + CartItem
│   ├── order.py              # Order + OrderItem
│   ├── review.py             # Product reviews
│   └── wishlist.py           # Customer wishlist
│
├── controllers/              # Business logic (C in MVC)
│   ├── auth_controller.py
│   ├── product_controller.py
│   ├── cart_controller.py
│   ├── order_controller.py
│   ├── seller_controller.py
│   └── admin_controller.py
│
├── routes/                   # URL routing (Flask Blueprints)
│   ├── auth.py               # /auth/*
│   ├── customer.py           # /, /products, /cart, /checkout
│   ├── seller.py             # /seller/*
│   └── admin.py              # /admin/*
│
├── templates/                # Jinja2 HTML templates (V in MVC)
│   ├── base.html             # Shared layout
│   ├── auth/                 # Login, Register
│   ├── customer/             # Home, Products, Cart, Checkout...
│   ├── seller/               # Dashboard, Products, Orders
│   ├── admin/                # Dashboard, Users, Products, Orders
│   └── errors/               # 404, 500
│
└── static/
    ├── css/main.css          # Premium white minimal theme
    ├── js/main.js            # Interactive features
    └── images/products/      # Uploaded product images
```

---

## Architecture

### MVC Pattern
- **Model**: `models/` — MongoDB documents with OOP encapsulation
- **View**: `templates/` — Jinja2 templates with Bootstrap 5
- **Controller**: `controllers/` — Business logic separated from routes

### OOP Principles
- **Encapsulation**: Each model encapsulates its data and DB operations
- **Inheritance**: Customer, Seller, Admin all extend base User concepts
- **Abstraction**: Controllers abstract business logic from route handlers
- **SOLID**: Single-responsibility classes per domain entity

### Database Collections
| Collection | Purpose |
|-----------|---------|
| users | All user accounts (customer/seller/admin) |
| products | Product listings |
| cart | Shopping carts (1 per user) |
| orders | Placed orders |
| reviews | Product reviews |
| wishlist | User wishlists |

---

## Features

### Customer
- Browse products with search + filter (category, price, size, brand)
- Product detail with gallery, reviews, related products
- Cart with promo codes (FASHION20, STYLE10, NEW15)
- Checkout with address + payment simulation
- Order tracking with timeline
- Wishlist management
- Star ratings and reviews

### Seller
- Dashboard with sales analytics
- Product CRUD with image upload
- Low stock alerts
- Order management

### Admin
- Platform KPI dashboard
- User/Seller management (activate/suspend)
- Product moderation
- Order status management

---

## Promo Codes
- `FASHION20` — 20% off
- `STYLE10` — 10% off
- `NEW15` — 15% off

---

*ICT602 Software Engineering — Assignment 3 | Group Project*
