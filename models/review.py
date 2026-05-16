from datetime import datetime
from bson import ObjectId
from database.db import get_db


class Review:
    """Customer review and star rating for a product."""

    def __init__(self, data: dict):
        self._id = data.get('_id')
        self.product_id = data.get('product_id')
        self.user_id = data.get('user_id')
        self.user_name = data.get('user_name', 'Anonymous')
        self.rating = int(data.get('rating', 5))
        self.title = data.get('title', '')
        self.comment = data.get('comment', '')
        self.created_at = data.get('created_at', datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            'product_id': self.product_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'created_at': self.created_at,
        }

    def save(self) -> str:
        db = get_db()
        if self._id:
            db.reviews.update_one({'_id': self._id}, {'$set': self.to_dict()})
            return str(self._id)
        result = db.reviews.insert_one(self.to_dict())
        self._id = result.inserted_id
        return str(self._id)

    @classmethod
    def get_by_product(cls, product_id, limit: int = 20) -> list:
        try:
            docs = get_db().reviews.find(
                {'product_id': ObjectId(product_id)}
            ).sort('created_at', -1).limit(limit)
            return [cls(d) for d in docs]
        except Exception:
            return []

    @classmethod
    def get_avg_rating(cls, product_id) -> tuple:
        """Returns (avg_rating, count)."""
        try:
            pipeline = [
                {'$match': {'product_id': ObjectId(product_id)}},
                {'$group': {'_id': None, 'avg': {'$avg': '$rating'}, 'count': {'$count': {}}}}
            ]
            result = list(get_db().reviews.aggregate(pipeline))
            if result:
                return round(result[0]['avg'], 1), result[0]['count']
            return 0, 0
        except Exception:
            return 0, 0

    @classmethod
    def user_reviewed(cls, product_id, user_id) -> bool:
        try:
            return get_db().reviews.find_one({
                'product_id': ObjectId(product_id),
                'user_id': user_id,
            }) is not None
        except Exception:
            return False
