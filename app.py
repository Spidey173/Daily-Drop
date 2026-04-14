"""
Daily Drop E-Commerce Application.

A Flask-based e-commerce platform for selling daily essentials and household items.
This module contains the main application routes and logic.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
from urllib.parse import urlparse, urljoin

from config import config_dict, Config
from database import (
    init_database, DatabaseError, get_user_by_email, get_user_by_id,
    get_all_products, get_product_by_id
)
from utils import (
    validate_user_input, is_valid_email, is_valid_phone,
    validate_order_data, validate_contact_data, sanitize_string
)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config_dict.get('development'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
try:
    init_database()
    logger.info("Database initialized successfully")
except DatabaseError as e:
    logger.error(f"Failed to initialize database: {e}")
    raise



# ==================== Helper Functions ====================

def is_safe_url(target: str) -> bool:
    """
    Validate if a URL is safe for redirect operations.

    Checks if the target URL belongs to the same origin to prevent
    open redirect vulnerabilities.

    Args:
        target: The URL to validate.

    Returns:
        True if URL is safe, False otherwise.
    """
    try:
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
    except Exception as e:
        logger.warning(f"Error validating URL: {e}")
        return False


def require_login(f):
    """
    Decorator to require user login for a route.

    Redirects to login page if user is not authenticated.
    """
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# ==================== Authentication Routes ====================

@app.route('/')
def intro() -> str:
    """Render the introductory page."""
    return render_template('intro.html')


@app.route('/index')
def index() -> str:
    """
    Render the home page with featured products.

    Returns:
        Rendered HTML template.
    """
    try:
        products = get_all_products()[:6]  # Get first 6 products
        return render_template('index.html', products=products)
    except DatabaseError as e:
        logger.error(f"Error fetching products: {e}")
        flash('Error loading products', 'error')
        return render_template('index.html', products=[])


@app.route('/signup', methods=['GET', 'POST'])
def signup() -> str:
    """
    Handle user registration.

    GET: Display signup form.
    POST: Process signup form and create new user account.

    Returns:
        Rendered signup template or redirect to login page.
    """
    if request.method == 'POST':
        try:
            name = sanitize_string(request.form.get('name', ''))
            email = sanitize_string(request.form.get('email', ''))
            password = request.form.get('password', '')

            # Validate input
            is_valid, error_msg = validate_user_input(name, email, password)
            if not is_valid:
                flash(error_msg, 'error')
                return render_template('signup.html')

            # Check if user exists
            if get_user_by_email(email):
                flash('Email already registered!', 'error')
                return render_template('signup.html')

            # Create user (in production, hash password using werkzeug.security)
            from database import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (name, email, password)
                    VALUES (?, ?, ?)
                ''', (name, email, password))

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except DatabaseError as e:
            logger.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login() -> str:
    """
    Handle user login.

    GET: Display login form.
    POST: Authenticate user and create session.

    Returns:
        Rendered login template or redirect to home page.
    """
    if 'user_id' in session:
        return redirect(url_for('index'))

    next_url = request.args.get('next') or request.form.get('next')

    if request.method == 'POST':
        try:
            email = sanitize_string(request.form.get('email', ''))
            password = request.form.get('password', '')

            # Validate inputs
            if not is_valid_email(email) or not password:
                flash('Invalid email or password', 'error')
                return render_template('login.html', next_url=next_url)

            # Get user from database
            user = get_user_by_email(email)

            if not user or user['password'] != password:
                logger.warning(f"Failed login attempt for email: {email}")
                flash('Invalid email or password', 'error')
                return render_template('login.html', next_url=next_url)

            # Create session
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session.permanent = True

            logger.info(f"User {email} logged in successfully")
            flash('Login successful!', 'success')

            # Safe redirect
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('index'))

        except DatabaseError as e:
            logger.error(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')

    return render_template('login.html', next_url=next_url)


@app.route('/logout')
def logout() -> str:
    """Clear user session and redirect to intro page."""
    session.clear()
    logger.info("User logged out")
    flash('You have been logged out.', 'info')
    return redirect(url_for('intro'))


# ==================== Product Routes ====================

@app.route('/vegetables')
def vegetables() -> str:
    """Display vegetables and fruits."""
    try:
        products = get_all_products('FruitsandVegetables')
        return render_template('Vegetables.html', products=products)
    except DatabaseError as e:
        logger.error(f"Error fetching vegetables: {e}")
        flash('Error loading products', 'error')
        return render_template('Vegetables.html', products=[])


@app.route('/grocery')
def grocery() -> str:
    """Display grocery products."""
    return render_template('Grocery.html')


@app.route('/home_kitchen')
def home_kitchen() -> str:
    """Display home and kitchen products."""
    return render_template('home_kitchen.html')


@app.route('/baby_care')
def baby_care() -> str:
    """Display baby care products."""
    return render_template('baby_care.html')


@app.route('/household_items')
def household_items() -> str:
    """Display household items."""
    return render_template('household_items.html')


@app.route('/personal_care')
def personal_care() -> str:
    """Display personal care products."""
    return render_template('personal_care.html')


@app.route('/snacks_beverages')
def snacks_beverages() -> str:
    """Display snacks and beverages."""
    try:
        products = get_all_products('Snacks and Beverages')
        return render_template('snacks_beverages.html', products=products)
    except DatabaseError as e:
        logger.error(f"Error fetching snacks: {e}")
        flash('Error loading products', 'error')
        return render_template('snacks_beverages.html', products=[])


@app.route('/dairy_breakfast')
def dairy_breakfast() -> str:
    """Display dairy and breakfast products."""
    try:
        products = get_all_products('Dairy and breakfast')
        return render_template('dairy_breakfast.html', products=products)
    except DatabaseError as e:
        logger.error(f"Error fetching dairy products: {e}")
        flash('Error loading products', 'error')
        return render_template('dairy_breakfast.html', products=[])


# ==================== Shopping Cart & Payment Routes ====================

@app.route('/cart')
def cart() -> str:
    """
    Display shopping cart page.

    Requires user to be logged in.
    """
    if 'user_id' not in session:
        return redirect(url_for('login', next=url_for('payment')))
    return render_template('cart.html')


@app.route('/payment')
@require_login
def payment() -> str:
    """Display payment page."""
    return render_template('payment.html')


@app.route('/place_order', methods=['POST'])
@require_login
def place_order() -> Tuple[Dict[str, Any], int]:
    """
    Process order placement.

    Validates order data, saves to database, and returns success response.

    Returns:
        JSON response with success status.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        # Extract and validate data
        full_name = sanitize_string(data.get('full_name', ''))
        phone_number = data.get('phone_number', '')
        address = sanitize_string(data.get('address', ''))
        products = data.get('products', [])
        total_amount = data.get('total_amount', 0)

        # Validate order data
        is_valid, error_msg = validate_order_data(full_name, phone_number, address, products)
        if not is_valid:
            logger.warning(f"Invalid order data: {error_msg}")
            return jsonify({'success': False, 'message': error_msg}), 400

        # Validate total amount
        try:
            total_amount = float(total_amount)
            if total_amount <= 0:
                raise ValueError("Invalid amount")
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid total amount'}), 400

        # Save order to database
        from database import get_db_connection
        products_json = json.dumps(products)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (user_id, full_name, phone_number, address, products_ordered, total_amount)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                full_name,
                phone_number,
                address,
                products_json,
                total_amount
            ))

        logger.info(f"Order placed by user {session['user_id']} for amount {total_amount}")
        return jsonify({'success': True}), 200

    except json.JSONDecodeError:
        logger.error("Invalid JSON in order request")
        return jsonify({'success': False, 'message': 'Invalid data format'}), 400
    except DatabaseError as e:
        logger.error(f"Database error while placing order: {e}")
        return jsonify({'success': False, 'message': 'Order processing failed'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in place_order: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500


@app.route('/orders')
@require_login
def orders() -> str:
    """
    Display user's order history.

    Returns:
        Rendered orders template.
    """
    try:
        from database import get_db_connection
        from datetime import datetime
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC',
                (session['user_id'],)
            )
            order_rows = cursor.fetchall()

        parsed_orders = []
        for order in order_rows:
            order_dict = dict(order)
            try:
                order_dict['products'] = json.loads(order_dict['products_ordered'])
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in order {order['order_id']}")
                order_dict['products'] = []
            # Convert order_date string to datetime object for template rendering
            if isinstance(order_dict.get('order_date'), str):
                try:
                    order_dict['order_date'] = datetime.fromisoformat(order_dict['order_date'])
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse date: {order_dict.get('order_date')}")
            parsed_orders.append(order_dict)

        return render_template('orders.html', orders=parsed_orders)

    except DatabaseError as e:
        logger.error(f"Error retrieving orders: {e}")
        flash('Error loading orders', 'error')
        return render_template('orders.html', orders=[])


# ==================== User & Contact Routes ====================

@app.route('/dashboard')
@require_login
def dashboard() -> str:
    """Display user dashboard."""
    return render_template('dashboard.html')


@app.route('/contact_us', methods=['GET', 'POST'])
@require_login
def contact_us() -> str:
    """
    Handle contact form submissions.

    GET: Display contact form.
    POST: Save contact message to database.

    Returns:
        Rendered contact template.
    """
    try:
        user = get_user_by_id(session['user_id'])

        if not user:
            flash('User not found. Please log in again.', 'error')
            return redirect(url_for('logout'))

        if request.method == 'POST':
            name = sanitize_string(request.form.get('name', user['name']))
            email = sanitize_string(request.form.get('email', user['email']))
            phone = request.form.get('phone', '')
            subject = sanitize_string(request.form.get('subject', ''))
            message = sanitize_string(request.form.get('message', ''))

            # Validate contact data
            is_valid, error_msg = validate_contact_data(name, email, subject, message)
            if not is_valid:
                flash(error_msg, 'error')
                return render_template('contact_us.html', user=user, name=name, email=email)

            # Save contact message
            from database import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO contact_messages (user_id, name, email, phone, subject, message)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session['user_id'], name, email, phone, subject, message))

            logger.info(f"Contact message received from {email}")
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact_us'))

        return render_template('contact_us.html', user=user)

    except DatabaseError as e:
        logger.error(f"Error in contact_us: {e}")
        flash('Error processing your request', 'error')
        return render_template('contact_us.html')


# ==================== Static Pages ====================

@app.route('/privacy_policy_signup')
def privacy_policy_signup() -> str:
    """Display privacy policy for signup page."""
    return render_template('privacy_policy_signup.html')


@app.route('/privacy_policy_login')
def privacy_policy_login() -> str:
    """Display privacy policy for login page."""
    return render_template('privacy_policy_login.html')


@app.route('/privacy_policy_signup_home')
def privacy_policy_signup_home() -> str:
    """Display privacy policy for home page signup."""
    return render_template('privacy_policy_signup_home.html')


@app.route('/terms_login')
def terms_login() -> str:
    """Display terms and conditions for login page."""
    return render_template('terms_login.html')


@app.route('/terms_signup')
def terms_signup() -> str:
    """Display terms and conditions for signup page."""
    return render_template('terms_signup.html')


@app.route('/terms_signup_home')
def terms_signup_home() -> str:
    """Display terms and conditions for home page signup."""
    return render_template('terms_signup_home.html')


@app.route('/faqs')
def faqs() -> str:
    """Display frequently asked questions."""
    return render_template('faqs.html')


@app.route('/about_us')
def about_us() -> str:
    """Display about us page."""
    return render_template('about_us.html')


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found_error(error) -> Tuple[str, int]:
    """Handle 404 errors."""
    logger.warning(f"404 error: {error}")
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error) -> Tuple[str, int]:
    """Handle 500 errors."""
    logger.error(f"500 error: {error}")
    return render_template('500.html'), 500


# ==================== Application Entry Point ====================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5003,
        debug=app.config['DEBUG']
    )
