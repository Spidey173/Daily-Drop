"""
Unit and integration tests for Cart & Orders Blueprint & OrderService.
"""
import pytest
import json
from app import create_app
from services.auth_service import AuthService
from services.order_service import OrderService
from database import get_db_connection, clear_user_cache


@pytest.fixture
def test_user():
    email = 'cart_test_user@example.com'
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE email = %s", (email,))
    clear_user_cache(email)

    success, msg, user_id = AuthService.register_user('Cart Tester', email, 'Password@1234')
    assert success is True and user_id is not None, f"Failed to setup test user: {msg}"
    yield user_id

    # Cleanup
    if user_id:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        clear_user_cache(email, user_id)


@pytest.fixture
def client(test_user):
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = test_user
            sess['name'] = 'Cart Tester'
            sess['email'] = 'cart_test_user@example.com'
            sess['user_role'] = 'customer'
        yield client


def test_cart_and_payment_views(client):
    res_cart = client.get('/cart')
    assert res_cart.status_code == 200

    res_payment = client.get('/payment')
    assert res_payment.status_code == 200


def test_order_creation_and_history(client, test_user):
    items = [
        {"name": "Organic Tomatoes", "price": 3.99, "quantity": 2},
        {"name": "Whole Milk", "price": 4.50, "quantity": 1}
    ]

    # 1. Place order via OrderService
    success, msg, order_id = OrderService.create_order(
        user_id=test_user,
        full_name='Cart Tester',
        phone_number='9876543210',
        address='789 Market Ave',
        products=items,
        total_amount=12.48
    )
    assert success is True
    assert order_id is not None

    # 2. Retrieve customer orders
    orders = OrderService.get_user_orders(test_user)
    assert len(orders) >= 1
    placed_order = next((o for o in orders if o['order_id'] == order_id), None)
    assert placed_order is not None
    assert len(placed_order['products']) == 2

    # 3. View orders page via HTTP
    res = client.get('/orders')
    assert res.status_code == 200


def test_place_order_endpoint(client):
    order_payload = {
        'full_name': 'Cart Tester',
        'phone_number': '1234567890',
        'address': '456 Test Blvd',
        'products': [{'name': 'Apple', 'price': 1.50, 'quantity': 3}],
        'total_amount': 4.50
    }
    res = client.post('/place_order', json=order_payload)
    assert res.status_code == 200
    res_json = res.get_json()
    assert res_json['success'] is True
