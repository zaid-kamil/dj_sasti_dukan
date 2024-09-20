"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views as mv
from cart import views as cv

urlpatterns = [
    path('admin/', admin.site.urls),
    # customer
    path('accounts/', include('allauth.urls')),
    path('login/customer', mv.customer_login_view, name='customer_login'),
    path('register/customer', mv.customer_register_view, name='customer_register'),
    path('forgot/customer', mv.customer_forgot_pass_view, name='customer_forgot_pass'),

    # seller
    path('login/seller', mv.seller_login_view, name='seller_login'),
    path('register/seller', mv.seller_register_view, name='seller_register'),
    path('forgot/seller', mv.seller_forgot_pass_view, name='seller_forgot_pass'),
    # common to both
    path('dashboard', mv.dashboard_selection_view, name='dashboard'),
    path('dashboard/customer', mv.customer_dashboard_view, name='cdashboard'),
    path('dashboard/seller', mv.seller_dashboard_view, name='sdashboard'),
    path('logout', mv.logout_view, name='logout'),
    # index
    path('', mv.home_view, name='home'),
    path('search', mv.search_view, name='search'), # search
    path('cat/<slug:name>', mv.category_view, name='category'),
    path('detail/<int:id>', mv.detail_view, name='detail'),
    path("__reload__/", include("django_browser_reload.urls")),
    # checkout
    path('payment/initiate', cv.initiate_payment, name='init_payment'),
    path('payment/callback', cv.callback, name='callback'),
    path('success/', cv.success_view, name='success'),
    path('failure/', cv.failure_view, name='failure'),

    # review
    path('review/add/<int:id>', mv.add_review, name='add_review'),
    path('review/edit/<int:id>', mv.edit_review, name='edit_review'),
    # cart
    path('cart/view', cv.view_cart, name='cart_view'),
    path('cart/add/<int:id>', cv.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:id>', cv.remove_from_cart, name='remove_from_cart'),
    path('cart/callback', cv.cart_callback, name='cart_callback'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
