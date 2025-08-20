from django import template
from book_app.models import Cart

register = template.Library()

@register.filter
def times(number):
    """
    Returns a range from 0 to number-1.
    Usage: {% for i in 5|times %} → loops 5 times.
    """
    try:
        return range(int(number))
    except (ValueError, TypeError):
        return []

@register.simple_tag
def cart_item_count(user):
    """Returns the total number of items in the user's cart."""
    if user.is_authenticated:
        return Cart.objects.filter(user=user).count()
    return 0

@register.filter
def subtract(value, arg):
    """
    Subtracts arg from value.
    Usage: {{ 5|subtract:2 }} → 3
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return ''
