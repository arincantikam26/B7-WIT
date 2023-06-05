from django.urls import path
from . import views

app_name = 'toko'

urlpatterns = [
    path('', views.HomeListView, name='home-produk-list'),
    path('product/<slug>/', views.ProductDetailView, name='produk-detail'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove_from_cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('shop/', views.ShopView, name='shop'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order-summary/', views.OrderCartView, name='order-summary'),
    path('contact/', views.ContactView, name='contact'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]