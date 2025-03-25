from django import template
from pprint import pformat

register = template.Library()

@register.filter
def proficiency_color(value):
    """숙련도에 따른 색상 클래스를 반환합니다."""
    if value < 2:
        return 'danger'
    elif value < 3:
        return 'warning'
    elif value < 4:
        return 'info'
    elif value < 5:
        return 'primary'
    return 'success'

@register.filter
def multiply(value, arg):
    """두 수를 곱합니다."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def calculate_progress(current, total):
    if total == 0:
        return 0
    return (current / total) * 100

@register.filter
def type(value):
    return value.__class__.__name__

@register.filter
def pprint(value):
    return pformat(value) 