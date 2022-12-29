from django.urls import re_path
from django.views.generic import RedirectView
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponsePermanentRedirect
from django.utils.html import escape

from .models import Menu, MenuItem


class MenuItemAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site, menu):
        super(MenuItemAdmin, self).__init__(model, admin_site)
        self._menu = menu

    def delete_view(self, request, object_id, extra_context=None):
        if request.method == 'POST':
            super(MenuItemAdmin, self).delete_view(request, object_id, extra_context)
            return HttpResponseRedirect("../../../")
        else:
            return super(MenuItemAdmin, self).delete_view(request, object_id, extra_context)

    def save_model(self, request, obj, form, change):
        obj.menu = self._menu
        obj.save()

    def response_add(self, request, obj, post_url_continue=None):
        pk_value = obj._get_pk_val()
        post_url_continue = f'../{pk_value}/'
        response = super(MenuItemAdmin, self).response_add(request, obj, post_url_continue)
        if "_continue" in request.POST:
            return response
        elif "_addanother" in request.POST:
            return HttpResponseRedirect(request.path)

        else:
            return HttpResponseRedirect("../../")

    def response_change(self, request, obj):
        super(MenuItemAdmin, self).response_change(request, obj)
        if "_continue" in request.POST:
            return HttpResponseRedirect(request.path)
        elif "_addanother" in request.POST:
            return HttpResponseRedirect("../add/")
        elif "_saveasnew" in request.POST:
            return HttpResponseRedirect("../%s/" % obj._get_pk_val())
        else:
            return HttpResponseRedirect("../../")


class MenuAdmin(admin.ModelAdmin):
    menu_item_admin_class = MenuItemAdmin

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [re_path(r'^(?P<menu_pk>[-\w]+)/items/add/$', self.admin_site.admin_view(self.add_menu_item)),
                   re_path(r'^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/$',
                           self.admin_site.admin_view(self.edit_menu_item)),
                   re_path(r'^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/delete/$',
                           self.admin_site.admin_view(self.delete_menu_item)),]
        my_urls += [
            re_path(r'^item_changelist/$',
                    RedirectView.as_view(url='/'),
                    name='menu_app_menuitem_changelist'),
            re_path(r'^(?P<menu_pk>[-\w]+)/items/add/$',
                    RedirectView.as_view(url='/'),
                    name='menu_app_menuitem_change'),
            re_path(r'^(?P<menu_pk>[-\w]+)/items/(?P<menu_item_pk>[-\w]+)/delete/$',
                    self.menu_item_redirect,
                    {'action': 'delete'},
                    name='menu_app_menuitem_delete'),
        ]
        return my_urls + urls

    def get_object_with_change_permissions(self, request, model, obj_pk):
        ''' Helper function that returns a menu/menuitem if it exists and if the user has the change permissions '''
        obj = model._default_manager.get(pk=obj_pk)
        if not self.has_change_permission(request, obj):
            raise PermissionDenied
        if obj is None:
            raise Http404('%s object with primary key %r does not exist.' % (model.__name__, escape(obj_pk)))
        return obj

    def menu_item_redirect(self, request, pk, action):
        menu_pk = MenuItem.objects.select_related('menu').get(id=pk).menu.id
        return HttpResponsePermanentRedirect(
            r'../../%d/items/%s/%s/' % (menu_pk, pk, action))

    def add_menu_item(self, request, menu_pk):
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menuitem_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menuitem_admin.add_view(request, extra_context={'menu': menu})

    def edit_menu_item(self, request, menu_pk, menu_item_pk):
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menu_item_admin.change_view(request, menu_item_pk, extra_context={'menu': menu})

    def delete_menu_item(self, request, menu_pk, menu_item_pk):
        menu = self.get_object_with_change_permissions(request, Menu, menu_pk)
        menu_item_admin = self.menu_item_admin_class(MenuItem, self.admin_site, menu)
        return menu_item_admin.delete_view(request, menu_item_pk, extra_context={'menu': menu})


admin.site.register(Menu, MenuAdmin)
