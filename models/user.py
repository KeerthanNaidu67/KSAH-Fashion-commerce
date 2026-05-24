# models/user.py
# User model for the KSAH Fashion E-Commerce platform.
# Represents all user accounts regardless of role (customer, seller, admin).
# Implements the Flask-Login user interface (is_authenticated, get_id, etc.)
# and provides class methods for database operations: find, create, count, save.
# Passwords are stored as bcrypt hashes via werkzeug.security.

from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db


class User:
    """Base User model — encapsulates authentication and profile data."""

    ROLES = ('customer', 'seller', 'admin')

    def __init__(self, data: dict):
        self._id = data.get('_id')
        self.email = data.get('email', '')
        self.name = data.get('name', '')
        self.phone = data.get('phone', '')
        self.role = data.get('role', 'customer')
        self.avatar = data.get('avatar', '')
        self.address = data.get('address', {})
        self.is_active = data.get('is_active', True)
        self.created_at = data.get('created_at', datetime.utcnow())
        self._password_hash = data.get('password_hash', '')

    # Flask-Login interface
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self._id)

    def set_password(self, password: str):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self._password_hash, password)

    def to_dict(self) -> dict:
        return {
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'role': self.role,
            'avatar': self.avatar,
            'address': self.address,
            'is_active': self.is_active,
            'password_hash': self._password_hash,
            'created_at': self.created_at,
        }

    # ── DB operations ──────────────────────────────────────────────

    @classmethod
    def find_by_email(cls, email: str):
        doc = get_db().users.find_one({'email': email.lower().strip()})
        return cls(doc) if doc else None

    @classmethod
    def find_by_id(cls, user_id: str):
        try:
            doc = get_db().users.find_one({'_id': ObjectId(user_id)})
            return cls(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def get_all(cls, role: str = None) -> list:
        query = {'role': role} if role else {}
        return [cls(d) for d in get_db().users.find(query).sort('created_at', -1)]

    @classmethod
    def count_by_role(cls, role: str) -> int:
        return get_db().users.count_documents({'role': role})

    def save(self) -> str:
        db = get_db()
        if self._id:
            # Update existing user document
            db.users.update_one({'_id': self._id}, {'$set': self.to_dict()})
            return str(self._id)
        # Insert new user and store the generated _id
        result = db.users.insert_one(self.to_dict())
        self._id = result.inserted_id
        return str(self._id)

    def delete(self):
        get_db().users.delete_one({'_id': self._id})

    def update_status(self, is_active: bool):
        self.is_active = is_active
        get_db().users.update_one({'_id': self._id}, {'$set': {'is_active': is_active}})

    @staticmethod
    def create(email: str, name: str, password: str, role: str = 'customer', **kwargs) -> 'User':
        user = User({
            'email': email.lower().strip(),
            'name': name,
            'role': role,
            **kwargs,
            'created_at': datetime.utcnow(),
        })
        user.set_password(password)
        user.save()
        return user
