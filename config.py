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
    SECRET_KEY = os.getenv('SECRET_KEY', 'daily-drop-neon-secure-key-2026')
    SESSION_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Database settings (Neon PostgreSQL)
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    DB_MIN_CONN = int(os.getenv('DB_MIN_CONN', 3))
    DB_MAX_CONN = int(os.getenv('DB_MAX_CONN', 15))
    DB_TIMEOUT = 30


    # Performance & Static asset caching
    SEND_FILE_MAX_AGE_DEFAULT = 43200  # 12 hours browser caching for static files
    TEMPLATES_AUTO_RELOAD = DEBUG

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


# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

