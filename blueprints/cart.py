"""
Cart and checkout blueprint managing shopping cart, payment, order placement, and history.
"""
from typing import Tuple, Dict, Any
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from services.order_service import OrderService
from blueprints.helpers import require_login
from extensions import csrf

logger = logging.getLogger(__name__)

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/cart', endpoint='cart')
def cart() -> str:
    """Display shopping cart page."""
    if 'user_id' not in session:
        flash('Please log in to access your cart!', 'error')
        return redirect(url_for('auth.login', next=url_for('cart.cart')))
    return render_template('cart.html')


@cart_bp.route('/payment', endpoint='payment')
@require_login
def payment() -> str:
    """Display payment page."""
    return render_template('payment.html')


@cart_bp.route('/place_order', methods=['POST'], endpoint='place_order')
@csrf.exempt
@require_login
def place_order() -> Tuple[Any, int]:
    """Process order placement."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data received'}), 400

    full_name = data.get('full_name', '')
    phone_number = data.get('phone_number', '')
    address = data.get('address', '')
    products = data.get('products', [])
    total_amount = data.get('total_amount', 0)

    success, message, order_id = OrderService.create_order(
        user_id=session['user_id'],
        full_name=full_name,
        phone_number=phone_number,
        address=address,
        products=products,
        total_amount=total_amount
    )

    if not success:
        return jsonify({'success': False, 'message': message}), 400

    return jsonify({'success': True, 'order_id': order_id, 'message': message}), 200


@cart_bp.route('/orders', endpoint='orders')
@require_login
def orders() -> str:
    """Display user's order history."""
    user_orders = OrderService.get_user_orders(session['user_id'])
    return render_template('orders.html', orders=user_orders)


# ==================== Wishlist Routes ====================

@cart_bp.route('/wishlist', endpoint='wishlist')
@require_login
def wishlist() -> str:
    """Display user's saved wishlist products."""
    from services.wishlist_service import WishlistService
    items = WishlistService.get_user_wishlist(session['user_id'])
    return render_template('wishlist.html', wishlist_items=items)


@cart_bp.route('/api/v1/wishlist/toggle', methods=['POST'], endpoint='api_toggle_wishlist')
@csrf.exempt
@require_login
def api_toggle_wishlist() -> Tuple[Any, int]:
    """Toggle item in wishlist via AJAX."""
    from services.wishlist_service import WishlistService
    data = request.get_json(silent=True) or request.form
    product_id = data.get('product_id')
    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid product ID'}), 400

    success, message, in_wishlist, count = WishlistService.toggle_item(session['user_id'], product_id)
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'in_wishlist': in_wishlist,
            'count': count,
            'product_id': product_id
        }), 200
    return jsonify({'success': False, 'message': message}), 400


@cart_bp.route('/api/v1/wishlist/remove', methods=['POST'], endpoint='api_remove_wishlist')
@csrf.exempt
@require_login
def api_remove_wishlist() -> Tuple[Any, int]:
    """Remove item from wishlist via AJAX."""
    from services.wishlist_service import WishlistService
    data = request.get_json(silent=True) or request.form
    product_id = data.get('product_id')
    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid product ID'}), 400

    success, message, count = WishlistService.remove_item(session['user_id'], product_id)
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'count': count,
            'product_id': product_id
        }), 200
    return jsonify({'success': False, 'message': message}), 400


@cart_bp.route('/api/v1/wishlist/ids', methods=['GET'], endpoint='api_wishlist_ids')
def api_wishlist_ids() -> Tuple[Any, int]:
    """Retrieve list of product IDs currently in user's wishlist."""
    from services.wishlist_service import WishlistService
    if 'user_id' not in session:
        return jsonify({'success': True, 'ids': [], 'count': 0, 'logged_in': False}), 200

    ids = WishlistService.get_user_wishlist_ids(session['user_id'])
    return jsonify({
        'success': True,
        'ids': ids,
        'count': len(ids),
        'logged_in': True
    }), 200

