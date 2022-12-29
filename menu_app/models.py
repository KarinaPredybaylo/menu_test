from itertools import chain

from django.db import models
from django.utils.translation import gettext, gettext_lazy as _


class MenuItem(models.Model):
    name = models.CharField(max_length=50)
    named_url = models.CharField(max_length=200, blank=True)
    level = models.IntegerField(default=0, editable=False)
    parent = models.ForeignKey('self', verbose_name=_('parent'), null=True, blank=True, on_delete=models.CASCADE)
    menu = models.ForeignKey('Menu', related_name='contained_items', verbose_name=_('menu'), null=True, blank=True,
                             editable=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, **kwargs):
        old_level = self.level
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0

        super(MenuItem, self).save(force_insert, **kwargs)

        if old_level != self.level:
            for child in self.children():
                child.save()

    def get_flattened(self):
        flat_structure = [self]
        for child in self.children():
            flat_structure = chain(flat_structure, child.get_flattened())
        return flat_structure

    def children(self):
        _children = MenuItem.objects.filter(parent=self)
        for child in _children:
            child.parent = self
        return _children

    def has_children(self):
        return self.children().count() > 0


class Menu(models.Model):
    name = models.CharField(max_length=50)
    root_item = models.ForeignKey(MenuItem, related_name='is_root_item_of', verbose_name=_('root item'), null=True,
                                  blank=True, editable=False, on_delete=models.CASCADE)

    def save(self, force_insert=False, **kwargs):
        if not self.root_item:
            root_item = MenuItem()
            root_item.name = gettext('root')
            if not self.pk:
                super(Menu, self).save(force_insert, **kwargs)
                force_insert = False
            root_item.menu = self
            root_item.save()
            self.root_item = root_item
        super(Menu, self).save(force_insert, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.root_item is not None:
            self.root_item.delete()
        super(Menu, self).delete()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('menu')
        verbose_name_plural = _('menus')
