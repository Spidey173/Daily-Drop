"""
Application configuration module.

This module contains centralized configuration settings for the Daily Drop
application, including database paths, Flask settings, and security parameters.
"""

import os
from datetime import timedelta

# Get environment or use defaults
ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = ENV == 'development'


class Config:
    """Base configuration."""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    SESSION_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'product_users.db')
    DB_TIMEOUT = 30

    # Pagination
    ITEMS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10

    # File uploads
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = True
    TESTING = True
    DATABASE_PATH = ':memory:'


# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
