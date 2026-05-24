# controllers/product_controller.py
# Product controller for the KSAH Fashion E-Commerce platform.
# Handles customer-facing product operations: home page data (featured +
# category previews), paginated product listing with filters, product detail
# view with reviews, and review submission with duplicate prevention.
# Used by routes/customer.py.

from models.product import Product
from models.review import Review
from bson import ObjectId


class ProductController:
    """Product browsing and detail logic."""

    @staticmethod
    def get_home_data() -> dict:
        featured = Product.get_featured(8)
        men = Product.get_by_category('Men', 4)
        women = Product.get_by_category('Women', 4)
        accessories = Product.get_by_category('Accessories', 4)
        return {
            'featured': featured,
            'men': men,
            'women': women,
            'accessories': accessories,
        }

    @staticmethod
    def get_product_list(request_args: dict) -> dict:
        filters = {}
        if request_args.get('category'):
            filters['category'] = request_args['category']
        if request_args.get('brand'):
            brands = request_args.getlist('brand')
            if brands:
                filters['brand'] = brands
        if request_args.get('min_price'):
            filters['min_price'] = float(request_args['min_price'])
        if request_args.get('max_price'):
            filters['max_price'] = float(request_args['max_price'])
        if request_args.get('size'):
            filters['size'] = request_args.getlist('size')
        if request_args.get('q'):
            filters['search'] = request_args['q']

        sort_by = request_args.get('sort', 'newest')
        page = max(1, int(request_args.get('page', 1)))
        per_page = 12

        products, total = Product.get_all(filters, sort_by, page, per_page)
        total_pages = (total + per_page - 1) // per_page

        return {
            'products': products,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'filters': filters,
            'sort_by': sort_by,
        }

    @staticmethod
    def get_product_detail(product_id: str) -> dict:
        product = Product.find_by_id(product_id)
        if not product:
            return None
        reviews = Review.get_by_product(product_id)
        avg_rating, review_count = Review.get_avg_rating(product_id)
        # Related products
        related, _ = Product.get_all({'category': product.category}, page=1, per_page=4)
        related = [p for p in related if str(p._id) != product_id][:4]
        return {
            'product': product,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_count': review_count,
            'related': related,
        }

    @staticmethod
    def submit_review(product_id: str, user, form_data: dict) -> tuple[bool, str]:
        if Review.user_reviewed(product_id, user._id):
            return False, 'You have already reviewed this product.'
        rating = int(form_data.get('rating', 5))
        if not 1 <= rating <= 5:
            return False, 'Rating must be between 1 and 5.'
        review = Review({
            'product_id': ObjectId(product_id),
            'user_id': user._id,
            'user_name': user.name,
            'rating': rating,
            'title': form_data.get('title', ''),
            'comment': form_data.get('comment', ''),
        })
        review.save()
        # Update product aggregate rating
        avg, count = Review.get_avg_rating(product_id)
        product = Product.find_by_id(product_id)
        if product:
            product.update_rating(avg, count)
        return True, 'Review submitted successfully!'
