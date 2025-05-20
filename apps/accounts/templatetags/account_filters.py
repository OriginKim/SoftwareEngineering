from django import template

register = template.Library()

@register.filter
def calculate_progress(value, total):
    """진행률을 계산하는 필터"""
    try:
        if total == 0:
            return 0
        return int((value / total) * 100)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """두 값을 뺄셈하는 필터"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0 