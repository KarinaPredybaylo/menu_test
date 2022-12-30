from django.shortcuts import render
from .models import Menu


def home(request):
    if request.method == 'GET':
        menu_objects = Menu.objects.all()
        context = {'menus': menu_objects}
        return render(request, 'index.html', context)


def menu_detail(request, name, id=None):
    menu_object = Menu.objects.get(name=name)
    items = menu_object.contained_items.all()
    context = {'menu': menu_object,
               'items': items}

    if id is not None:
        item_ac = menu_object.contained_items.get(id=id)
        ids = [item_ac.parent.id]
        if item_ac.level > 2:
            ids.append(item_ac.parent.parent.id)
        print(ids)
        if str(item_ac.id) in request.path:
            context['active_item'] = item_ac
            context['ids'] = ids

    return render(request, 'menu.html', context)
