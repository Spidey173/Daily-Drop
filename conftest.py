import sys
import os
import pytest

# Add root project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


@pytest.fixture(autouse=True)
def check_db_availability(request):
    """
    Check if the test requires database access and skip gracefully if DB is unavailable.
    """
    from database import get_pool, DatabaseError
    # If the test is purely route unit test without DB, let it run
    if request.node.name in ['test_home_page', 'test_product_routes']:
        return
    try:
        get_pool()
    except DatabaseError as e:
        pytest.skip(f"Database connection pool unavailable: {e}")

