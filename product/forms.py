from django import forms
from .models import Product,Category,Review

# model form -> form that is created from a model
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category','image', 'title',
                'description', 'price', 'brand']
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content', 'rating']