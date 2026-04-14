"""
Database module for handling all database operations.

This module provides database connection management, initialization,
and helper functions for CRUD operations with proper error handling
and SQL parameterization.
"""

import sqlite3
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

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    description TEXT
                )
            ''')

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
                    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

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

            logger.info("Database initialized successfully")
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
