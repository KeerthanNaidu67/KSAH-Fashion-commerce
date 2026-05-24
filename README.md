# KSAH — Fashion E-Commerce Platform

A full-stack fashion e-commerce web application built with Python Flask, MongoDB, and Bootstrap 5, following the MVC architectural pattern. The platform supports three user roles — Customer, Seller, and Admin — each with dedicated dashboards and role-based access control.

> ICT602 Software Engineering — Group Project 3

---

## Table of Contents

- [Team Members](#team-members)
- [Tech Stack](#tech-stack)
- [Features](#features)
  - [Customer](#customer)
  - [Seller](#seller)
  - [Admin](#admin)
- [Security](#security)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create and Activate Virtual Environment](#2-create-and-activate-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Configure Environment Variables](#4-configure-environment-variables)
  - [5. Seed the Database](#5-seed-the-database)
  - [6. Run the App](#6-run-the-app)
- [Demo Credentials](#demo-credentials)
- [Promo Codes](#promo-codes)
- [Project Structure](#project-structure)
- [Database Collections](#database-collections)
- [Architecture](#architecture)
- [Testing](#testing)

---

## Team Members

| Name | Student ID | Role |
|---|---|---|
| Shaik Mohammed Hayath | 65939 | Project Lead — Database layer, models, seller dashboard |
| Janyavula Sai Keerthan | 66041 | Second Lead — App foundation, authentication, product browsing |
| Md Atiqul Islam Akash | 65868 | Cart, checkout, order management |
| Rafikul Haque | 67168 | Admin panel, shared UI layout, error handling |

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
- Product reviews and star ratings (1–5)

### Seller
- Seller dashboard with real-time sales statistics
- Add, edit, and delete product listings
- Product image upload with file type validation
- View orders containing seller's own products

### Admin
- Admin dashboard with platform-wide statistics and monthly revenue
- User management — activate or suspend customer/seller accounts
- Product moderation — activate or deactivate listings
- Order status management across all orders

---

## Security

- Passwords are securely hashed using Werkzeug's `generate_password_hash` before storage — no plain-text passwords are saved in MongoDB
- Role-based access control via per-blueprint decorators (`seller_required`, `admin_required`) prevents unauthorized access
- File uploads validated against an allowed extension whitelist before saving
- Suspended accounts are blocked from logging in

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

### 4. Configure Environment Variables

Create a `.env` file in the root directory of the `fashion-ecommerce` project. You can copy the provided example file:

```bash
cp .env.example .env
```

Open `.env` and adjust the variables as needed:

| Variable | Description | Default / Example Value |
|---|---|---|
| `SECRET_KEY` | Flask session encryption and security key | `fashion-ecommerce-secret-change-this-in-production` |
| `MONGO_URI` | MongoDB connection string URI | `mongodb://localhost:*****/fashion_ecommerce` |
| `FLASK_ENV` | Application environment status | `development` |
| `FLASK_DEBUG` | Enable Flask debug mode (`1` for enabled, `0` for disabled) | `1` |
| `PORT` | The port on which the web application runs | `9***` |

### 5. Seed the Database
```bash
python database/seed.py
```

### 6. Run the App
```bash
python app.py
```

Visit: **http://localhost:9090** (or the port configured in `.env`)

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
├── app.py                    # Flask application factory — registers blueprints, error handlers
├── config.py                 # DevelopmentConfig / ProductionConfig
├── requirements.txt
│
├── database/
│   ├── db.py                 # Singleton MongoDB connection via get_db()
│   └── seed.py               # Demo data seeder (users, products, orders, reviews)
│
├── models/                   # Model layer (M in MVC)
│   ├── user.py               # User model — auth, roles, profile
│   ├── product.py            # Product model — listing, filtering, stock
│   ├── cart.py               # Cart + CartItem — add, remove, promo codes
│   ├── order.py              # Order + OrderItem — checkout, tracking
│   ├── review.py             # Product reviews and star ratings
│   └── wishlist.py           # Customer saved products
│
├── controllers/              # Controller layer (C in MVC)
│   ├── auth_controller.py    # Registration, login, logout
│   ├── product_controller.py # Product listing, detail, review submission
│   ├── cart_controller.py    # Cart CRUD, promo codes, wishlist toggle
│   ├── order_controller.py   # Checkout, order history, cancellation
│   ├── seller_controller.py  # Seller dashboard, product CRUD, image upload
│   └── admin_controller.py   # Dashboard stats, user/product/order management
│
├── routes/                   # Flask Blueprints — URL mapping
│   ├── auth.py               # /auth/login, /auth/register, /auth/logout
│   ├── customer.py           # /, /products, /cart, /checkout, /orders, /wishlist
│   ├── seller.py             # /seller/dashboard, /seller/products, /seller/orders
│   └── admin.py              # /admin/dashboard, /admin/users, /admin/products, /admin/orders
│
├── templates/                # View layer — Jinja2 HTML (V in MVC)
│   ├── base.html             # Shared layout with navbar, cart badge, Bootstrap 5
│   ├── auth/                 # login.html, register.html
│   ├── customer/             # home, products, product_detail, cart, checkout, orders, wishlist
│   ├── seller/               # dashboard, products, add_product, edit_product, orders
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
| `cart` | Active shopping carts (one per user) |
| `orders` | Placed orders with embedded items and status tracking |
| `reviews` | Product reviews and star ratings |
| `wishlist` | Customer saved product references |

---

## Architecture

The application follows the **MVC (Model-View-Controller)** pattern combined with a **Client-Server** architecture:

- **Model** — `models/` handles all data and MongoDB operations
- **View** — `templates/` renders HTML via Jinja2, no business logic
- **Controller** — `controllers/` contains all business logic
- **Routes** — `routes/` maps URLs to controllers via Flask Blueprints

```
Browser → Routes (Blueprint) → Controller → Model → MongoDB
                                    ↓
                              Jinja2 Template → Browser
```

---

## Testing

- **40 manual test cases** covering all three user roles
- **White Box Testing** — branch coverage and boundary value analysis on controller logic
- **Black Box Testing** — use case testing and equivalence partitioning through the UI
- All 40 test cases passed
- Full test report: `testing/test_report.md`
