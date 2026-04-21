from django.shortcuts import render
from store.models import Product
from store.recommender import get_recommendations

def home(request):
    products = Product.objects.all().filter(is_available=True)

    # Get recommended products for the user (or general trending if not logged in)
    recommended_products = get_recommendations(user=request.user, limit=8)

    context = {
        'products': products,
        'recommended_products': recommended_products,
    }

    return render(request, 'home.html', context)