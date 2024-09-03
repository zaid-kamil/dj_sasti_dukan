from django.contrib import admin
from .models import Category, Product, Review

# creating admin dashboard
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)