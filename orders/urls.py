from django.urls import path, include
from . import views


urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('khalti-initiate/', views.khalti_initiate, name='khalti_initiate'),
    path('khalti-callback/', views.khalti_callback, name='khalti_callback'),
]
