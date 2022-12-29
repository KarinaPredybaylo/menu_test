from django.urls import re_path, path
from . import views

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    path('<str:name>/', views.menu_detail, name='detail_menu'),
    path('<str:name>/<int:id>', views.menu_detail, name='detail_menu_item'),
]
