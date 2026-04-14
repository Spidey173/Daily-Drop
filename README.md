# 🛒 Daily Drop - E-Commerce Platform

> A modern Flask-based e-commerce application for ordering daily essentials and household items with fast delivery.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Project Routes](#project-routes)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Daily Drop** is a full-featured e-commerce platform designed to simplify online shopping for daily essentials such as groceries, household items, personal care products, and baby care items. Users can browse products, create accounts, manage their cart, place orders, and make payments—all through an intuitive web interface.

The application is built with Flask, a lightweight Python web framework, and uses SQLite for data persistence, making it easy to deploy and maintain.

---

## ✨ Features

### User Management
- ✅ User registration and authentication (signup/login)
- ✅ Secure password handling
- ✅ Session management with automatic expiration
- ✅ User profile management

### Shopping Experience
- 🛍️ Browse products across multiple categories:
  - Grocery & Daily Staples
  - Dairy & Breakfast
  - Fruits & Vegetables
  - Household Items
  - Personal Care
  - Baby Care
  - Snacks & Beverages
  - Kitchen Essentials
- 🔍 Product search and filtering
- 📦 Shopping cart functionality (add/remove items)
- 💳 Secure checkout process

### Orders & Payments
- 📲 Order placement and tracking
- 💰 Payment processing integration
- 📜 Order history and status updates
- 🧾 Order details and invoicing

### Additional Features
- 📧 Contact form for customer support
- 📖 About Us and FAQs pages
- 📋 Privacy Policy and Terms of Service
- 🖼️ Product images and category sections
- 📱 Responsive web design

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Framework** | Flask 2.3.3 |
| **Database** | SQLite3 |
| **Web Server** | Gunicorn 21.2.0 |
| **Frontend** | HTML5, Jinja2 Templates |
| **HTTP Utilities** | Werkzeug 3.1.3 |
| **CORS Support** | Flask-CORS 4.0.0 |
| **Environment Management** | python-dotenv 1.0.0 |
| **Testing** | pytest 7.4.0, pytest-cov 4.1.0 |

---

## 📁 Project Structure

```
Daily Drop/
├── app.py                      # Main Flask application & routes
├── config.py                   # Configuration settings
├── database.py                 # Database operations & schema
├── dashboard.py                # Dashboard/admin functionality
├── utils.py                    # Utility functions & validators
├── reinit_db.py               # Database re-initialization script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .venv/                     # Virtual environment (local)
│
├── static/                    # Static assets
│   ├── image/                # Product & decorative images
│   ├── Baby Care/            # Category-specific images
│   ├── Dairy and breakfast/
│   ├── FruitsandVegetables/
│   ├── Grocery/
│   ├── household/
│   ├── kitchen/
│   ├── personal care/
│   ├── Snacks/
│   ├── Tomato/
│   └── slider/               # Homepage slider images
│
├── templates/                # HTML templates
│   ├── index.html           # Homepage
│   ├── intro.html           # Introduction page
│   ├── login.html           # User login
│   ├── signup.html          # User registration
│   ├── cart.html            # Shopping cart
│   ├── payment.html         # Payment page
│   ├── orders.html          # Order history
│   ├── about_us.html        # About page
│   ├── contact_us.html      # Contact form
│   ├── faqs.html            # FAQ section
│   ├── privacy_policy_*.html # Privacy policies
│   ├── terms_*.html         # Terms & conditions
│   └── [category].html      # Category pages
│
└── product_users.db         # SQLite database (auto-created)
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment tool (venv)

### Steps

1. **Clone the Repository**
   ```bash
   cd /Users/spidey./Desktop/Daily\ Drop
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate Virtual Environment**
   ```bash
   # macOS/Linux
   source .venv/bin/activate
   
   # Windows
   .venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize Database**
   ```bash
   python reinit_db.py
   ```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

```env
# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_PATH=product_users.db
DB_TIMEOUT=30

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=5242880  # 5MB in bytes

# Session Configuration
SESSION_COOKIE_SECURE=False     # Set to True in production
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### Configuration Classes

The app supports multiple configurations via `config.py`:

- **DevelopmentConfig**: Debug enabled, suitable for local development
- **ProductionConfig**: Debug disabled, optimized for deployment
- **Custom Configs**: Extend the base `Config` class as needed

---

## 🏃 Usage

### Running the Application

```bash
# Development mode with Flask development server
python app.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Accessing the Application

Open your browser and navigate to:
```
http://localhost:5000
```

### Common Operations

- **Homepage**: View all products and categories
- **Browse Categories**: Explore items by category
- **Create Account**: Sign up with email and password
- **Add to Cart**: Click "Add to Cart" on product pages
- **Checkout**: Review cart and proceed to payment
- **View Orders**: Check order history in user dashboard

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    image_url TEXT,
    stock_quantity INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Orders Table
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL FOREIGN KEY,
    status TEXT DEFAULT 'Pending',
    total_amount REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Contact Messages Table
```sql
CREATE TABLE contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

---

## 🗺️ Project Routes

### Public Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Homepage |
| `/intro` | GET | Introduction page |
| `/about` | GET | About Us page |
| `/faqs` | GET | FAQ section |
| `/contact` | GET/POST | Contact form |
| `/privacy` | GET | Privacy policy |
| `/terms` | GET | Terms & conditions |

### Authentication Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/signup` | GET/POST | User registration |
| `/login` | GET/POST | User login |
| `/logout` | GET | User logout |

### Product Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/products` | GET | All products listing |
| `/products/<category>` | GET | Products by category |
| `/product/<id>` | GET | Product details |

### Cart & Order Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/cart` | GET | View shopping cart |
| `/cart/add/<product_id>` | POST | Add item to cart |
| `/cart/remove/<product_id>` | POST | Remove item from cart |
| `/checkout` | GET/POST | Checkout process |
| `/payment` | GET/POST | Payment page |
| `/orders` | GET | View order history |
| `/order/<id>` | GET | Order details |

---

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_auth.py
```

---

## 📝 Code Quality

### Input Validation
The `utils.py` module provides comprehensive validation functions:
- Email validation
- Phone number validation
- User input sanitization
- Order data validation
- Contact form validation

### Security Features
- SQL parameterization to prevent SQL injection
- Password hashing
- Secure session cookies (HTTPOnly, SameSite)
- CSRF protection
- Input sanitization
- XSS prevention

### Error Handling
- Custom `DatabaseError` exception class
- Comprehensive logging throughout the application
- Graceful error messages for users
- Database transaction management

---

## 🔧 Development

### Adding New Features

1. **New Category**: Add images to `static/[category]`, create template in `templates/`
2. **New Route**: Update `app.py` with Flask route decorator
3. **New Database Table**: Modify `database.py` and `reinit_db.py`
4. **New Validation**: Add function to `utils.py`

### Debugging

Enable detailed logging in development:
```python
logging.basicConfig(level=logging.DEBUG)
```

Check logs for detailed error messages and database operations.

---

## 📦 Dependencies Management

### Adding New Package

1. Install locally: `pip install package-name`
2. Add to `requirements.txt`: `pip freeze > requirements.txt`
3. Commit changes

### Updating Packages

```bash
pip install --upgrade -r requirements.txt
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Update `SECRET_KEY` to a strong random value
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Configure proper database backups
- [ ] Set up SSL/TLS certificates
- [ ] Use Gunicorn behind reverse proxy (nginx/Apache)
- [ ] Configure logging to files
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Enable database connection pooling for high traffic

### Deployment Command

```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Document functions with docstrings
- Keep functions focused and modular
- Add comments for complex logic

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For issues, questions, or feature requests:

- 📧 Use the Contact Us form in the application
- 🐛 Report bugs in the Issues section
- 💬 Discussion section for feature ideas

---

## 🎉 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Database powered by [SQLite](https://www.sqlite.org/)
- Deployed with [Gunicorn](https://gunicorn.org/)

---

**Last Updated**: April 2024  
**Version**: 1.0.0  
**Status**: Active Development
