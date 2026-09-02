"""
Order service managing checkout, order history retrieval, status updates, and analytics.
"""
from typing import Optional, List, Dict, Any, Tuple
import json
import time
import logging
from datetime import datetime
from database import (
    get_db_connection, DatabaseError, get_all_orders_with_user_info,
    update_order_status as db_update_order_status, get_dashboard_stats,
    get_sales_data, get_category_revenue, get_hourly_order_distribution
)
from utils import validate_order_data, sanitize_string

logger = logging.getLogger(__name__)

_ANALYTICS_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_ANALYTICS_TTL = 60.0  # 60 seconds in-memory cache for ultra-fast admin dashboard


class OrderService:
    """Service providing order placement, history tracking, and sales analytics."""


    @staticmethod
    def create_order(user_id: int, full_name: str, phone_number: str, address: str,
                     products: Any, total_amount: float) -> Tuple[bool, str, Optional[int]]:
        """
        Validate and save a customer order.

        Returns:
            Tuple of (success, message, order_id).
        """
        full_name = sanitize_string(full_name)
        address = sanitize_string(address)

        is_valid, error_msg = validate_order_data(full_name, phone_number, address, products)
        if not is_valid:
            return False, error_msg, None

        try:
            total_amount = float(total_amount)
            if total_amount <= 0:
                return False, 'Invalid total amount', None
        except (ValueError, TypeError):
            return False, 'Invalid total amount format', None

        products_json = json.dumps(products) if not isinstance(products, str) else products

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO orders (user_id, full_name, phone_number, address, products_ordered, total_amount, status)
                        VALUES (%s, %s, %s, %s, %s, %s, 'Processing')
                        RETURNING order_id
                    ''', (user_id, full_name, phone_number, address, products_json, total_amount))
                    order_id = cursor.fetchone()[0]

            _ANALYTICS_CACHE.clear()
            logger.info(f"Order #{order_id} placed successfully by user #{user_id}")
            return True, 'Order placed successfully', order_id
        except DatabaseError as e:
            logger.error(f"Error saving order: {e}")
            return False, 'Failed to save order to database', None

    @staticmethod
    def get_user_orders(user_id: int) -> List[Dict[str, Any]]:
        """Retrieve order history for a customer."""
        from psycopg2.extras import RealDictCursor
        try:
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        'SELECT * FROM orders WHERE user_id = %s ORDER BY order_date DESC',
                        (user_id,)
                    )
                    order_rows = cursor.fetchall()

            parsed_orders = []
            for order in order_rows:
                order_dict = dict(order)
                try:
                    order_dict['products'] = json.loads(order_dict['products_ordered'])
                except Exception:
                    order_dict['products'] = []
                if isinstance(order_dict.get('order_date'), str):
                    try:
                        order_dict['order_date'] = datetime.fromisoformat(order_dict['order_date'])
                    except Exception:
                        pass
                parsed_orders.append(order_dict)

            return parsed_orders
        except DatabaseError as e:
            logger.error(f"Error fetching orders for user #{user_id}: {e}")
            return []

    @staticmethod
    def get_all_orders() -> List[Dict[str, Any]]:
        """Retrieve all orders with user info for admin dashboard."""
        try:
            return get_all_orders_with_user_info()
        except DatabaseError as e:
            logger.error(f"Error fetching all orders: {e}")
            return []

    @staticmethod
    def update_status(order_id: int, status: str) -> Tuple[bool, str]:
        """Update status of an order."""
        valid_statuses = ['Processing', 'Packed', 'Shipped', 'Out for Delivery', 'Delivered', 'Cancelled']
        if status not in valid_statuses:
            return False, f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"

        try:
            success = db_update_order_status(order_id, status)
            if success:
                _ANALYTICS_CACHE.clear()
                return True, f"Order #{order_id} status updated to {status}"
            return False, f"Order #{order_id} not found"
        except DatabaseError as e:
            logger.error(f"Error updating status for order #{order_id}: {e}")
            return False, 'Failed to update order status'

    @staticmethod
    def get_analytics(days: int = 30) -> Dict[str, Any]:
        """Retrieve full administrative analytics with in-memory caching for sub-millisecond dashboard responses."""
        now = time.time()
        cache_key = f"analytics_{days}"
        if cache_key in _ANALYTICS_CACHE:
            cached_time, cached_data = _ANALYTICS_CACHE[cache_key]
            if now - cached_time < _ANALYTICS_TTL:
                return cached_data

        try:
            stats = get_dashboard_stats()
            sales = get_sales_data(days)
            categories = get_category_revenue()
            hourly = get_hourly_order_distribution()
            analytics_data = {
                'stats': stats,
                'sales': sales,
                'categories': categories,
                'hourly': hourly
            }
            _ANALYTICS_CACHE[cache_key] = (now, analytics_data)
            return analytics_data
        except DatabaseError as e:
            logger.error(f"Error retrieving analytics: {e}")
            return {}

