from django import template
from ..models import Menu

register = template.Library()


@register.inclusion_tag('menu.html', takes_context=True)
def show_menu(context, menu_name):
    menu = Menu.objects.get(name=menu_name)
    context['menu'] = menu
    context['menu_name'] = menu_name

    return context
