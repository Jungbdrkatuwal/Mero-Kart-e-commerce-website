from orders.models import OrderProduct
from .models import Product
from django.db.models import Count

def get_recommendations(product_id=None, user=None, limit=4):
    recommendations = []
    
    # 1. Collaborative filtering: "Users who bought this also bought"
    if product_id:
        orders_with_product = OrderProduct.objects.filter(product_id=product_id).values_list('order_id', flat=True)
        collab_products = OrderProduct.objects.filter(order__in=orders_with_product)\
            .exclude(product_id=product_id)\
            .values('product')\
            .annotate(buy_count=Count('product'))\
            .order_by('-buy_count')[:limit]
        
        for item in collab_products:
            try:
                p = Product.objects.get(id=item['product'], is_available=True)
                if p not in recommendations:
                    recommendations.append(p)
            except Product.DoesNotExist:
                pass
                
    # 2. Content-based: Same category
    if product_id and len(recommendations) < limit:
        try:
            current_product = Product.objects.get(id=product_id)
            similar_products = Product.objects.filter(category=current_product.category, is_available=True)\
                .exclude(id=product_id)\
                .order_by('?')[:limit - len(recommendations)]
            for p in similar_products:
                if p not in recommendations:
                    recommendations.append(p)
        except Product.DoesNotExist:
            pass

    # 3. User-based: "Recommended for you" based on their past orders
    if user and user.is_authenticated and not product_id and len(recommendations) < limit:
        user_categories = Product.objects.filter(orderproduct__user=user).values_list('category', flat=True).distinct()
        user_recs = Product.objects.filter(category__in=user_categories, is_available=True)\
            .exclude(orderproduct__user=user)\
            .order_by('?')[:limit - len(recommendations)]
        for p in user_recs:
            if p not in recommendations:
                recommendations.append(p)

    # 4. Fallback: Best Sellers / Trending
    if len(recommendations) < limit:
        best_sellers = OrderProduct.objects.values('product')\
            .annotate(buy_count=Count('product'))\
            .order_by('-buy_count')[:limit]
        
        for item in best_sellers:
            if len(recommendations) >= limit: break
            try:
                p = Product.objects.get(id=item['product'], is_available=True)
                if p not in recommendations:
                    recommendations.append(p)
            except Product.DoesNotExist:
                pass
                
    # 5. Absolute fallback: Latest products
    if len(recommendations) < limit:
        latest = Product.objects.filter(is_available=True).order_by('-created_date')[:limit]
        for p in latest:
            if len(recommendations) >= limit: break
            if p not in recommendations:
                recommendations.append(p)

    return recommendations[:limit]
