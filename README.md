# Daily Drop

An open-source Flask e-commerce web application for daily essentials and household products. The system provides category-based catalog browsing, client-side cart persistence, order processing, and a glassmorphic administration dashboard for inventory management, fulfillment status updates, and sales analytics.

## Key Features

- **Category Catalog Browsing**: Product catalog partitioned across 10 distinct categories (Fruits & Vegetables, Grocery, Home & Kitchen, Baby Care, Household, Personal Care, Snacks, Dairy & Breakfast, Beverages, Frozen Foods).
- **Client-Side Cart Management**: State synchronization via `localStorage` with checkout submission handling.
- **Role-Based Session Management**: Distinct authentication flows and access controls for customer and administrator sessions.
- **Administrative Control Panel**: Glassmorphic dashboard (`/admin/dashboard`) providing real-time sales metrics, inventory low-stock alerts, category revenue breakdowns, and order activity charts.
- **Catalog & Inventory REST API**: Endpoints for dynamic price updates, stock adjustments, product creation with image upload handling, and catalog deletion.
- **Order Fulfillment Tracking**: Endpoints to update customer order statuses (`Processing`, `Shipped`, `Delivered`, `Cancelled`).
- **Customer Inquiry Handling**: Form validation and SQLite storage for user contact messages.

## Architecture Overview

Daily Drop is structured as a monolithic Web Application built with Python and Flask.

```
+-------------------------------------------------------------------+
|                            Client                                 |
|   (Browser / HTML5 / Vanilla JS / localStorage Cart / Chart.js)   |
+---------------------------------+---------------------------------+
                                  |
                                  | HTTP / REST
                                  v
+---------------------------------+---------------------------------+
|                       Flask Application                           |
|  +---------------------+ +------------------+ +----------------+  |
|  | Authentication /    | | Product Catalog  | | Admin REST     |  |
|  | Session Management  | | & Cart Routes    | | & Analytics    |  |
|  +----------+----------+ +--------+---------+ +-------+--------+  |
|             |                     |                 |             |
|             +---------------------+-----------------+             |
|                                   |                               |
|                                   v                               |
|                     Database Context Manager                      |
+---------------------------------+---------------------------------+
                                  |
                                  | sqlite3 API
                                  v
+---------------------------------+---------------------------------+
|                       SQLite Database                             |
|       (users, products, orders, contact_messages tables)          |
+-------------------------------------------------------------------+
```

### Architectural Choices & Trade-offs

- **Monolithic Web Architecture**: Application logic, template rendering, and REST endpoints reside in a unified Flask app.
  - *Rationale*: Eliminates microservice complexity, reduces deployment overhead, and simplifies transaction management.
  - *Trade-off*: Tightly couples backend routing with Jinja2 rendering, limiting independent frontend deployment.
- **SQLite Database with Context Management**: Database operations utilize Python's `sqlite3` context manager (`get_db_connection()`) to ensure automatic connection closing and transactional commits/rollbacks.
  - *Rationale*: Serverless setup with zero database server administration required for development and low-to-medium traffic.
  - *Trade-off*: SQLite locks the database file on write operations, limiting write concurrency compared to client-server databases like PostgreSQL.
- **Client-Side Cart with Server Validation**: Cart items reside in browser `localStorage` and are transmitted as JSON payloads during checkout.
  - *Rationale*: Reduces server session state overhead and minimizes server memory consumption during catalog navigation.
  - *Trade-off*: Requires strict server-side validation (`validate_order_data`) on incoming checkout payloads to prevent tampering with item pricing or quantities.

## Tech Stack

| Layer | Component | Version / Details | Purpose |
|---|---|---|---|
| **Backend Framework** | Flask | `2.3.3` | Application routing, request handling, and template rendering |
| **WSGI Server** | Gunicorn | `21.2.0` | Production UNIX WSGI HTTP server |
| **Database** | SQLite3 | Native Python stdlib | Embedded relational data store (`product_users.db`) |
| **HTTP Utilities** | Werkzeug | `3.1.3` | Request/response handling and security utilities |
| **CORS Middleware** | Flask-CORS | `4.0.0` | Cross-Origin Resource Sharing control |
| **Environment** | python-dotenv | `1.0.0` | Environment variable management |
| **Frontend** | Jinja2 / JS | Jinja2 `3.1.6`, ES6 JS | Dynamic server-side rendering and client-side cart logic |
| **Testing** | Pytest | `7.4.0` (Dependency) | Testing framework (test suite to be implemented) |

## Project Structure

```
Daily-Drop/
├── app.py                      # Application entry point, route definitions, and REST endpoints
├── config.py                   # Environment configuration classes (Development, Production, Testing)
├── database.py                 # SQLite schema initialization, connection context manager, and CRUD operations
├── dashboard.py                # Standalone metrics and dashboard rendering helper script
├── utils.py                    # Validation, regex sanitization, and normalization functions
├── reinit_db.py                # Database schema resets and seed data loader
├── requirements.txt            # Python dependencies
├── .env.example                # Blueprint for local environment variables
├── static/                     # Static web assets
│   ├── css/                    # Component and page stylesheets (main.css)
│   ├── js/                     # Client-side scripts (cart.js, products.js)
│   └── uploads/                # User and admin uploaded product images
└── templates/                  # Jinja2 HTML templates
    ├── admin_dashboard.html    # Administrative analytics control panel
    ├── admin_orders.html       # Customer order management interface
    ├── cart.html               # Shopping cart view
    ├── checkout.html           # Checkout and payment submission view
    ├── index.html              # Storefront landing page
    └── ...                     # Category-specific template views
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- virtualenv (recommended)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/username/daily-drop.git
   cd daily-drop
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   *On Windows:*
   ```cmd
   venv\Scripts\activate
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration (.env example)

Copy `.env.example` to create your local `.env` file:

```bash
cp .env.example .env
```

Configuration variables supported by `config.py`:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_PATH=product_users.db
DB_TIMEOUT=30

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production

# Pagination Settings
ITEMS_PER_PAGE=12
ORDERS_PER_PAGE=10
```

## Running Locally

### Quick Start with `run.sh` (Recommended)

You can use the built-in management script [`run.sh`](file:///Users/spidey./Desktop/Daily-Drop/run.sh) to automatically set up the virtual environment, install dependencies, prepare configuration, initialize the database, and start the app:

```bash
# Make script executable (if not already)
chmod +x run.sh

# Run development server (default port: 5004)
./run.sh

# Or start on a custom port
./run.sh dev -p 8080

# Run in production mode with Gunicorn
./run.sh prod

# Reset or re-seed the SQLite database
./run.sh reset-db

# View all commands and options
./run.sh --help
```

### Manual Execution

1. Initialize the SQLite database and seed catalog data:
   ```bash
   python -c "from database import init_database; init_database()"
   ```

2. Start the development server:
   ```bash
   python app.py
   ```
   The application will be accessible at `http://localhost:5004`.

3. Run with Gunicorn (UNIX production environment):
   ```bash
   gunicorn --bind 0.0.0.0:5004 app:app
   ```

## Docker Setup

Docker configuration files (`Dockerfile` and `docker-compose.yml`) are not currently included in the repository. See [Future Improvements](#future-improvements) for containerization plans.

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description | Query Parameters / Body |
|---|---|---|---|
| `GET` | `/api/v1/products/list` | Retrieve product catalog | `category` (optional filter) |

### Customer Endpoints (Session Required)

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `POST` | `/place_order` | Submit order | JSON: `{ "full_name": str, "phone_number": str, "address": str, "products": list, "total_amount": float }` |

### Admin Endpoints (Admin Session Required)

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/api/v1/admin/analytics` | Fetch analytics dashboard metrics | None |
| `POST`/`PATCH` | `/api/v1/admin/orders/<id>/status` | Update order status | JSON / Form: `{ "status": str }` |
| `POST`/`PATCH` | `/api/v1/admin/products/<id>/price` | Update product price | JSON / Form: `{ "price": float }` |
| `POST`/`PATCH` | `/api/v1/admin/products/<id>/stock` | Update stock quantity | JSON / Form: `{ "stock": int }` |
| `POST` | `/api/v1/admin/products/add` | Add new product | Form data / Multipart (with optional `image_file`) |
| `POST`/`DELETE` | `/api/v1/admin/products/<id>/delete` | Delete catalog item | None |

## Screenshots

![Storefront Landing Page](docs/images/homepage_placeholder.png)
*Storefront displaying product catalog grid and category navigation.*

![Admin Analytics Dashboard](docs/images/admin_dashboard_placeholder.png)
*Glassmorphic administrative control panel with live metric charts.*

![Shopping Cart & Checkout](docs/images/cart_checkout_placeholder.png)
*Client-side cart itemization and order placement interface.*

## Example Usage

### Fetch Catalog via REST API

```bash
curl -X GET "http://localhost:5004/api/v1/products/list?category=Grocery"
```

Sample Response:
```json
{
  "success": true,
  "count": 12,
  "products": [
    {
      "product_id": 1,
      "name": "Organic Whole Milk",
      "price": 3.99,
      "category": "Grocery",
      "subcategory": "Dairy",
      "image_path": "/static/dairy-breakfast/milk.webp",
      "description": "Fresh organic whole milk 1 gal",
      "stock": 42
    }
  ]
}
```

### Submit Order via REST API

```bash
curl -X POST "http://localhost:5004/place_order" \
  -H "Content-Type: application/json" \
  -b "session=YOUR_SESSION_COOKIE" \
  -d '{
    "full_name": "Jane Doe",
    "phone_number": "+15550192834",
    "address": "123 Main St, Springfield",
    "products": [{"id": 1, "title": "Organic Whole Milk", "price": 3.99, "quantity": 2}],
    "total_amount": 7.98
  }'
```

## Design Decisions

- **Database Connection Lifecycle**: The `get_db_connection()` context manager handles connection acquisition, configuration (`row_factory = sqlite3.Row`), transaction commit on success, rollback on exception, and guaranteed socket closure.
- **Sanitization & Boundary Checks**: String inputs are sanitized and capped at 500 characters using `sanitize_string()` in `utils.py` to bound memory footprint and limit unexpected input payloads.
- **Host Validation on Redirection**: Post-authentication redirects execute host checking via `is_safe_url()` using `urlparse` and `urljoin` to prevent open-redirect exploits.

## Performance Considerations

- **Database File Locking**: SQLite executes file-level locking during write operations. Under concurrent write workloads, requests wait up to the configured `DB_TIMEOUT` (30 seconds) before failing.
- **Static File Delivery**: Static assets (`/static`) are currently served via Flask's built-in WSGI handler. For higher throughput deployments, offloading static file serving to Nginx or a CDN is recommended.

## Security Considerations

- **Open Redirect Guard**: Internal redirect targets passed via `?next=` are validated against the current host.
- **Parameterized Database Queries**: SQL statements in `database.py` use parameterized placeholders (`?`) to prevent SQL injection.
- **Session Cookie Properties**: Session cookies configure `HttpOnly=True`, `SameSite=Lax`, and enforce `Secure=True` under production configurations (`ProductionConfig`).

## Testing

Dependencies `pytest` (`7.4.0`) and `pytest-cov` (`4.1.0`) are specified in `requirements.txt`.

*Current Repository Status*: The automated test suite is not yet implemented. Creating test coverage for route handlers, database helper methods, and API validation is planned under [Future Improvements](#future-improvements).

## Known Limitations

- **Plain-Text Password Storage**: Account passwords are currently verified via exact string comparison without cryptographic hashing functions (e.g., `pbkdf2:sha256` or `bcrypt`).
- **In-Memory Session Storage**: Flask sessions rely on server secret key signing without a centralized session database or key-value store (e.g., Redis), preventing zero-downtime deployment across multiple independent nodes.
- **Concurrency Constraints**: SQLite write locking limits scalability under simultaneous multi-user checkout traffic.

## Future Improvements

- [ ] Implement password hashing using `werkzeug.security` (`generate_password_hash` / `check_password_hash`).
- [ ] Construct automated unit and integration test suite using `pytest` covering API endpoints and authentication flows.
- [ ] Add `Dockerfile` and `docker-compose.yml` for multi-container orchestration.
- [ ] Migrate database layer to PostgreSQL via Flask-SQLAlchemy to support concurrent write scaling and migration tracking.
- [ ] Implement CSRF token protection on form submissions using Flask-WTF.
- [ ] Integrate Redis for distributed session storage and catalog caching.

## Contributing

Contributions are welcome. Please adhere to the following workflow:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit changes with concise, descriptive commit messages.
4. Push to your branch: `git push origin feature/your-feature-name`
5. Open a Pull Request outlining proposed changes.

## License

This project is currently provided without a formal open-source license. See `LICENSE` once added.
