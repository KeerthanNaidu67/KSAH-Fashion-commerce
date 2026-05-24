# config.py
# Application configuration classes for the KSAH Fashion E-Commerce platform.
# Defines base Config with shared settings, and DevelopmentConfig / ProductionConfig
# subclasses. The 'config' dict maps environment names to their config class.
# Values are read from environment variables (via .env) with sensible defaults.

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fashion-ecommerce-secret-key-ict602-2026')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/fashion_ecommerce')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)   # keep users logged in for 7 days
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024            # max upload size: 16 MB
    UPLOAD_FOLDER = os.path.join('static', 'images', 'products')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}  # permitted image types


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
