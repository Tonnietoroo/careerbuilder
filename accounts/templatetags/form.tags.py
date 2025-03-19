from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name="addclass")
def addclass(value, css_class):
    if isinstance(value, BoundField):  # Ensure it's a Django form field
        return value.as_widget(attrs={"class": css_class})
    return value  # If it's a string or something else, return it unchanged
