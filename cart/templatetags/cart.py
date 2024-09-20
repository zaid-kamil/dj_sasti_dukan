# cart custom template tags
from django.template import Library
from cart.models import Cart, CartItem

register = Library()

@register.simple_tag(takes_context=True)
def cart_count(context):
    request = context['request']
    # check user is logged in
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            return cart.cartitem_set.count()
    return 0