"""
Products blueprint handling catalog listings, categories, and product query APIs.
"""
import logging
from flask import Blueprint, render_template, request, jsonify
from services.product_service import ProductService

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__)


@products_bp.route('/vegetables', endpoint='vegetables')
def vegetables() -> str:
    """Display Vegetables category products."""
    products = ProductService.get_products_by_category('Vegetables')
    return render_template('Vegetables.html', products=products)


@products_bp.route('/grocery', endpoint='grocery')
def grocery() -> str:
    """Display Grocery category products."""
    products = ProductService.get_products_by_category('Grocery')
    return render_template('grocery.html', products=products)


@products_bp.route('/home_kitchen', endpoint='home_kitchen')
def home_kitchen() -> str:
    """Display Home & Kitchen category products."""
    products = ProductService.get_products_by_category('Home & Kitchen')
    return render_template('home_kitchen.html', products=products)


@products_bp.route('/baby_care', endpoint='baby_care')
def baby_care() -> str:
    """Display Baby Care category products."""
    products = ProductService.get_products_by_category('Baby Care')
    return render_template('baby_care.html', products=products)


@products_bp.route('/household_items', endpoint='household_items')
def household_items() -> str:
    """Display Household Items category products."""
    products = ProductService.get_products_by_category('Household')
    return render_template('household_items.html', products=products)


@products_bp.route('/personal_care', endpoint='personal_care')
def personal_care() -> str:
    """Display Personal Care category products."""
    products = ProductService.get_products_by_category('Personal Care')
    return render_template('personal_care.html', products=products)


@products_bp.route('/snacks', endpoint='snacks')
def snacks() -> str:
    """Display Snacks category products."""
    products = ProductService.get_products_by_category('Snacks')
    return render_template('snacks.html', products=products)


@products_bp.route('/dairy_breakfast', endpoint='dairy_breakfast')
def dairy_breakfast() -> str:
    """Display Dairy & Breakfast category products."""
    products = ProductService.get_products_by_category('Dairy & Breakfast')
    return render_template('dairy_breakfast.html', products=products)


@products_bp.route('/beverages', endpoint='beverages')
def beverages() -> str:
    """Display Beverages category products."""
    products = ProductService.get_products_by_category('Beverages')
    return render_template('beverages.html', products=products)


@products_bp.route('/frozen_foods', endpoint='frozen_foods')
def frozen_foods() -> str:
    """Display Frozen Foods category products."""
    products = ProductService.get_products_by_category('Frozen Foods')
    return render_template('frozen_foods.html', products=products)


@products_bp.route('/api/v1/products/list', methods=['GET'], endpoint='api_list_products')
def api_list_products():
    """API endpoint to get list of products with optional category and search filters."""
    category = request.args.get('category')
    search = request.args.get('search', '').lower().strip()

    products = ProductService.get_products_by_category(category)
    if search:
        products = [p for p in products if search in p['name'].lower() or search in (p.get('description') or '').lower()]

    return jsonify({
        'success': True,
        'count': len(products),
        'products': products
    }), 200


@products_bp.route('/api/v1/products/search', methods=['GET'], endpoint='api_search_products')
def api_search_products():
    """Live autocomplete search API returning matched products with limit."""
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 8)
    try:
        limit = min(int(limit), 20)
    except (TypeError, ValueError):
        limit = 8

    if not query:
        return jsonify({'success': True, 'count': 0, 'results': []}), 200

    results = ProductService.search_products(query, limit=limit)
    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    }), 200

