from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    # path('resetPassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
]