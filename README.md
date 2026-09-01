# DailyDrop 🛒

DailyDrop is a modern, high-performance e-commerce web application for grocery and daily essentials delivery. Built with Flask and Neon PostgreSQL, it features an intuitive customer storefront, persistent shopping cart, customer wishlist, instant live search autocomplete, interactive AI product metrics, and a dedicated admin management dashboard.

🔗 **[Live Demo](https://daily-drop-c96q-f5su.onrender.com/)**

---

## 🌟 Highlights & Contributions
- **Led a 4-member team** through Agile sprints to build DailyDrop, a full-stack Flask e-commerce app with cart, checkout, and admin dashboard workflows.
- **Designed the relational database schema** for accounts, carts, and orders, implementing role-based session management for customers and administrators.
- **Coordinated task ownership** across frontend and backend modules, resolved cross-module API integration issues, and reviewed teammates’ code to maintain consistent schema and endpoint design.

---

## ✨ Features

### 🛍️ Customer Storefront
- **Categorized Catalog**: 240+ products across 10 distinct categories (Vegetables, Fruits, Dairy, Beverages, Snacks, Frozen Foods, Household, Home & Kitchen, Personal Care, Baby Care).
- **🔍 Instant Live Search**: Real-time autocomplete dropdown in navigation bar with product thumbnails and instant "+ Add" to cart buttons.
- **❤️ Customer Wishlist**: Save favorite products with 1-click heart buttons and manage them on a dedicated Wishlist page.
- **📊 AI Quality & Safety Radar**: Dynamic product detail modals featuring live quality, safety, and nutritional metrics (Chart.js).
- **🛒 Smart Shopping Cart**: Real-time cart management with local storage persistence and quick order placement.

### 🛡️ Admin Control Panel (`/admin_login`)
- **Telemetry & Analytics**: Overview of total revenue, order count, user registrations, category breakdown, and peak ordering hours.
- **Inventory Management**: Update product prices, restock items, or add new catalog entries.
- **Order Fulfillment**: Track and update live order statuses (`Processing`, `Shipped`, `Delivered`, `Cancelled`).

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, Flask (Modular Blueprints, Service Layer Architecture)
- **Database**: Neon PostgreSQL (Connection Pooling, Sub-Millisecond In-Memory Caching)
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphic UI Theme), JavaScript (ES6+), Chart.js, Bootstrap 5
- **Security & Speed**: Werkzeug Password Hashing, Flask-WTF CSRF Protection, Flask-Limiter Rate Limiting
- **Deployment**: Gunicorn, Render IaC (`render.yaml`, `Procfile`)

---

## 📁 Project Structure

```
Daily-Drop/
├── app.py                  # Application factory (create_app)
├── database.py             # Neon PostgreSQL pooling and caching engine
├── config.py               # Environment configuration
├── extensions.py           # CSRF and Rate Limiter extensions
├── blueprints/             # Modular route handlers (auth, main, products, cart, admin)
├── services/               # Core business logic (auth, product, order, wishlist, contact)
├── static/                 # CSS styles, JS modules, product images
├── templates/              # HTML templates (Jinja2)
├── tests/                  # Automated pytest test suites
└── Procfile / render.yaml  # Deployment configuration
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- `pip` package manager

### 1. Clone & Setup
```bash
git clone https://github.com/Spidey173/Daily-Drop.git
cd Daily-Drop
```

### 2. Create Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (macOS/Linux):
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Application
```bash
# Start Flask dev server
python app.py
```
> Open [http://localhost:5000](http://localhost:5000) in your browser.

*(Optional)* You can also start the server using `./run.sh`.

---

## 🔑 Demo Credentials

Quick evaluation logins with 1-Click Auto-Fill on the login page:

| Role | Email | Password | Access URL | Features |
| :--- | :--- | :--- | :--- | :--- |
| **Demo Customer** | `demo_dailydrop@gmail.com` | `Demouser@123` | [`/login`](http://localhost:5000/login) | Storefront browsing, live search, wishlist, cart & checkout |
| **Demo Admin** | `admin_dailydrop@gmail.com` | `Dailydrop@173` | [`/admin_login`](http://localhost:5000/admin_login) | Analytics dashboard, inventory management, order processing |

---

## 🧪 Testing

Run unit & integration test suites:
```bash
pytest -v
```

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
