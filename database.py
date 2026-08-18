"""
Database module for handling all database operations.

This module provides database connection management, initialization,
and helper functions for CRUD operations with proper error handling
and SQL parameterization.
"""

import sqlite3
import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from contextlib import contextmanager

from config import Config

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations."""

    pass


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.

    Ensures proper connection handling and resource cleanup.

    Yields:
        sqlite3.Connection: Database connection with row factory set.

    Raises:
        DatabaseError: If connection fails.
    """
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH, timeout=Config.DB_TIMEOUT)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseError(f"Database error: {e}") from e
    finally:
        conn.close()


def init_database() -> None:
    """
    Initialize database with required tables.

    Creates tables for users, products, orders, and contact_messages
    if they don't exist.

    Raises:
        DatabaseError: If database initialization fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Create users table with role column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'customer',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Ensure role column exists if users table was created previously without role
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [col[1] for col in cursor.fetchall()]
            if 'role' not in user_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'customer'")

            # Create products table with stock column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    image_path TEXT NOT NULL,
                    description TEXT,
                    stock INTEGER DEFAULT 50
                )
            ''')

            # Ensure stock column exists if products table was created previously without stock
            cursor.execute("PRAGMA table_info(products)")
            product_columns = [col[1] for col in cursor.fetchall()]
            if 'stock' not in product_columns:
                cursor.execute("ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 50")

            # Create orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    full_name TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    address TEXT NOT NULL,
                    products_ordered TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'Processing',
                    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Ensure status column exists if orders table was created previously without status
            cursor.execute("PRAGMA table_info(orders)")
            order_columns = [col[1] for col in cursor.fetchall()]
            if 'status' not in order_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'Processing'")

            # Create contact_messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    subject TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Seed or update admin user credentials
            cursor.execute("SELECT id FROM users WHERE role = 'admin' OR email = 'admin_dailydrop@gmail.com' OR email = 'admin@dailydrop.com'")
            admin_user = cursor.fetchone()
            if not admin_user:
                cursor.execute('''
                    INSERT INTO users (name, email, password, role)
                    VALUES ('Admin User', 'admin_dailydrop@gmail.com', 'Dailydrop@173', 'admin')
                ''')
            else:
                cursor.execute('''
                    UPDATE users SET email = 'admin_dailydrop@gmail.com', password = 'Dailydrop@173', role = 'admin'
                    WHERE id = ?
                ''', (admin_user['id'],))

            # Seed products table from static/js/products.js if empty
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0] or 0
            if product_count == 0:
                js_file_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'products.js')
                if os.path.exists(js_file_path):
                    try:
                        with open(js_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        start = content.find('[')
                        end = content.rfind(']') + 1
                        if start != -1 and end != -1:
                            raw_products = json.loads(content[start:end])
                            for p in raw_products:
                                pid = p.get('id', 1)
                                unique_stock = (pid * 17 + 11) % 95
                                cursor.execute('''
                                    INSERT INTO products (product_id, name, price, category, subcategory, image_path, description, stock)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    pid,
                                    p.get('title', 'Product'),
                                    float(p.get('price', 0)),
                                    p.get('category', 'Grocery'),
                                    p.get('subcategory', ''),
                                    p.get('image', '/static/logo.webp'),
                                    p.get('description', ''),
                                    unique_stock
                                ))
                            logger.info(f"Seeded {len(raw_products)} products into SQLite database from products.js with unique stock values")
                    except Exception as e:
                        logger.error(f"Error seeding products from products.js: {e}")

            logger.info("Database initialized successfully with updated Admin credentials and catalog products")
    except DatabaseError as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by email address.

    Args:
        email: User's email address.

    Returns:
        Dictionary containing user data if found, None otherwise.

    Raises:
        DatabaseError: If database query fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE email = ?',
                (email,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None
    except sqlite3.Error as e:
        logger.error(f"Error retrieving user by email: {e}")
        raise DatabaseError(f"Failed to retrieve user: {e}") from e


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by ID.

    Args:
        user_id: User's ID.

    Returns:
        Dictionary containing user data if found, None otherwise.

    Raises:
        DatabaseError: If database query fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None
    except sqlite3.Error as e:
        logger.error(f"Error retrieving user by ID: {e}")
        raise DatabaseError(f"Failed to retrieve user: {e}") from e


def get_all_products(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all products, optionally filtered by category.

    Args:
        category: Optional category filter.

    Returns:
        List of product dictionaries.

    Raises:
        DatabaseError: If database query fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    'SELECT * FROM products WHERE category = ? ORDER BY name',
                    (category,)
                )
            else:
                cursor.execute('SELECT * FROM products ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error retrieving products: {e}")
        raise DatabaseError(f"Failed to retrieve products: {e}") from e


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a product by ID.

    Args:
        product_id: Product's ID.

    Returns:
        Dictionary containing product data if found, None otherwise.

    Raises:
        DatabaseError: If database query fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM products WHERE product_id = ?',
                (product_id,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None
    except sqlite3.Error as e:
        logger.error(f"Error retrieving product: {e}")
        raise DatabaseError(f"Failed to retrieve product: {e}") from e


def get_dashboard_stats() -> Dict[str, Any]:
    """
    Retrieve dashboard statistics.

    Returns:
        Dictionary containing various dashboard metrics.

    Raises:
        DatabaseError: If database query fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            total_orders = cursor.execute(
                'SELECT COUNT(*) FROM orders'
            ).fetchone()[0] or 0

            total_users = cursor.execute(
                'SELECT COUNT(*) FROM users'
            ).fetchone()[0] or 0

            total_products = cursor.execute(
                'SELECT COUNT(*) FROM products'
            ).fetchone()[0] or 0

            total_contacts = cursor.execute(
                'SELECT COUNT(*) FROM contact_messages'
            ).fetchone()[0] or 0

            total_revenue = cursor.execute(
                'SELECT SUM(total_amount) FROM orders'
            ).fetchone()[0] or 0

            avg_order_value = round(
                total_revenue / total_orders, 2
            ) if total_orders > 0 else 0

            return {
                'total_orders': total_orders,
                'total_users': total_users,
                'total_products': total_products,
                'total_contacts': total_contacts,
                'total_revenue': total_revenue,
                'avg_order_value': avg_order_value,
            }
    except sqlite3.Error as e:
        logger.error(f"Error retrieving dashboard stats: {e}")
        raise DatabaseError(f"Failed to retrieve stats: {e}") from e


def get_sales_data(days: int = 30) -> Dict[str, Any]:
    """
    Retrieve sales data for the specified number of days.

    Args:
        days: Number of days to retrieve (default: 30).

    Returns:
        Dictionary with labels, data, min_date, and max_date.

    Raises:
        DatabaseError: If database query fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days - 1)

            # Generate date range
            date_list = []
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

            # Query daily sales
            cursor.execute('''
                SELECT DATE(order_date) as sale_date, SUM(total_amount) as daily_total
                FROM orders
                WHERE DATE(order_date) BETWEEN ? AND ?
                GROUP BY sale_date
                ORDER BY sale_date
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

            daily_sales = cursor.fetchall()

            # Convert to dictionary
            sales_dict = {row['sale_date']: row['daily_total'] for row in daily_sales}

            # Fill missing dates with 0
            sales_data = [sales_dict.get(date, 0) for date in date_list]

            return {
                'labels': date_list,
                'data': sales_data,
                'min_date': start_date.strftime('%Y-%m-%d'),
                'max_date': end_date.strftime('%Y-%m-%d')
            }
    except sqlite3.Error as e:
        logger.error(f"Error retrieving sales data: {e}")
        raise DatabaseError(f"Failed to retrieve sales data: {e}") from e


# ==================== Admin Product CRUD Helpers ====================

def update_product_price(product_id: int, price: float) -> bool:
    """Update a product's price."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE products SET price = ? WHERE product_id = ?',
                (price, product_id)
            )
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating product price: {e}")
        raise DatabaseError(f"Failed to update product price: {e}") from e


def update_product_stock(product_id: int, stock: int) -> bool:
    """Update a product's stock quantity."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE products SET stock = ? WHERE product_id = ?',
                (stock, product_id)
            )
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating product stock: {e}")
        raise DatabaseError(f"Failed to update product stock: {e}") from e


def add_product(name: str, price: float, category: str, subcategory: str = '',
                image_path: str = '/static/logo.webp', description: str = '', stock: int = 50) -> int:
    """Add a new product to the database catalog."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, price, category, subcategory, image_path, description, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, price, category, subcategory, image_path, description, stock))
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error adding new product: {e}")
        raise DatabaseError(f"Failed to add product: {e}") from e


def delete_product(product_id: int) -> bool:
    """Delete a product by ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM products WHERE product_id = ?',
                (product_id,)
            )
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error deleting product: {e}")
        raise DatabaseError(f"Failed to delete product: {e}") from e


def get_low_stock_products(threshold: int = 10) -> List[Dict[str, Any]]:
    """Retrieve products where stock is equal to or below the given threshold."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM products WHERE stock <= ? ORDER BY stock ASC',
                (threshold,)
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error retrieving low stock products: {e}")
        raise DatabaseError(f"Failed to retrieve low stock products: {e}") from e


def get_all_orders_with_user_info() -> List[Dict[str, Any]]:
    """Retrieve all orders joined with customer details for Admin Dashboard."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT o.*, COALESCE(u.email, 'customer@dailydrop.com') as user_email
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                ORDER BY o.order_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error retrieving all orders for admin: {e}")
        raise DatabaseError(f"Failed to retrieve orders: {e}") from e


def update_order_status(order_id: int, status: str) -> bool:
    """Update order delivery status."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE orders SET status = ? WHERE order_id = ?',
                (status, order_id)
            )
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating order status: {e}")
        raise DatabaseError(f"Failed to update order status: {e}") from e


def get_category_revenue() -> Dict[str, float]:
    """Retrieve total sales revenue broken down by product category."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT products_ordered FROM orders')
            rows = cursor.fetchall()

            category_totals = {
                'Grocery': 0.0,
                'Vegetables': 0.0,
                'Dairy & Breakfast': 0.0,
                'Snacks': 0.0,
                'Beverages': 0.0,
                'Frozen Foods': 0.0,
                'Household': 0.0,
                'Home & Kitchen': 0.0,
                'Personal Care': 0.0,
                'Baby Care': 0.0
            }

            for row in rows:
                try:
                    items = json.loads(row['products_ordered'])
                    for item in items:
                        name = item.get('name', '')
                        price = float(item.get('price', 0))
                        qty = int(item.get('quantity', 1))

                        p_row = cursor.execute('SELECT category FROM products WHERE name = ?', (name,)).fetchone()
                        cat = p_row['category'] if p_row else 'Grocery'
                        category_totals[cat] = round(category_totals.get(cat, 0.0) + (price * qty), 2)
                except Exception:
                    continue

            return category_totals
    except sqlite3.Error as e:
        logger.error(f"Error retrieving category revenue: {e}")
        return {}


def get_hourly_order_distribution() -> Dict[str, int]:
    """Retrieve order volume across hours of the day (00:00 - 23:00)."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT strftime('%H', order_date) as order_hour, COUNT(*) as count
                FROM orders
                GROUP BY order_hour
            ''')
            rows = cursor.fetchall()
            hour_counts = {f"{h:02d}:00": 0 for h in range(24)}
            for r in rows:
                if r['order_hour'] is not None:
                    h_str = f"{int(r['order_hour']):02d}:00"
                    hour_counts[h_str] = r['count']
            return hour_counts
    except sqlite3.Error as e:
        logger.error(f"Error retrieving hourly distribution: {e}")
        return {}



