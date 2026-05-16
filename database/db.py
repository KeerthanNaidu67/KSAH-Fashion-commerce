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
            self._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self._client.admin.command('ping')
            self._db = self._client[db_name]
            self._create_indexes()
            print(f"✓ Connected to MongoDB: {db_name}")
        except ConnectionFailure as e:
            print(f"✗ MongoDB connection failed: {e}")
            raise

    def _create_indexes(self):
        db = self._db
        db.users.create_index('email', unique=True)
        db.products.create_index([('name', ASCENDING)])
        db.products.create_index([('category', ASCENDING)])
        db.products.create_index([('seller_id', ASCENDING)])
        db.products.create_index([('price', ASCENDING)])
        db.orders.create_index([('user_id', ASCENDING)])
        db.reviews.create_index([('product_id', ASCENDING)])
        db.cart.create_index('user_id', unique=True)

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
