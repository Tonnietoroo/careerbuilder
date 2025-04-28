from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(field, css_class):
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field 