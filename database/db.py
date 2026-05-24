# database/db.py
# MongoDB connection manager for the KSAH Fashion E-Commerce platform.
# Implements a singleton Database class so that only one MongoClient is created
# for the entire application lifetime. Also creates all required collection indexes
# on first connect for fast querying. The module-level get_db() helper is used
# throughout models to access the database instance.

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
import os


class Database:
    """Singleton MongoDB connection manager."""

    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self, uri: str, db_name: str = 'fashion_ecommerce'):
        try:
            # Connect with a 5-second timeout to fail fast on bad URI
            self._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self._client.admin.command('ping')  # verify connection is alive
            self._db = self._client[db_name]
            self._create_indexes()
            print(f"✓ Connected to MongoDB: {db_name}")
        except ConnectionFailure as e:
            print(f"✗ MongoDB connection failed: {e}")
            raise

    def _create_indexes(self):
        # Create indexes on startup to speed up common queries
        db = self._db
        db.users.create_index('email', unique=True)           # enforce unique emails
        db.products.create_index([('name', ASCENDING)])
        db.products.create_index([('category', ASCENDING)])   # fast category filtering
        db.products.create_index([('seller_id', ASCENDING)])  # fast seller product lookup
        db.products.create_index([('price', ASCENDING)])      # fast price sorting
        db.orders.create_index([('user_id', ASCENDING)])      # fast order history lookup
        db.reviews.create_index([('product_id', ASCENDING)])  # fast review lookup per product
        db.cart.create_index('user_id', unique=True)          # one cart per user

    @property
    def db(self):
        return self._db

    def get_collection(self, name: str):
        return self._db[name]

    def close(self):
        if self._client:
            self._client.close()


db_instance = Database()


def get_db():
    return db_instance.db
