#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path
from django.contrib.staticfiles import views as static_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required
import library.views as views
from .views import CustomLoginView, create_category_ajax, delete_category_ajax

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', CustomLoginView.as_view(), name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.user_register, name='user_register'),
    path('change_password/', login_required(views.change_password), name='change_password'),
    path('profile/', login_required(views.profile), name='profile'),

    path('static/<path:path>/', static_views.serve, name='static'),

    path('search/', views.search_books, name='search_books'),

    path('delete_category_ajax/', delete_category_ajax, name='delete_category_ajax'),
    path('create_category_ajax/', create_category_ajax, name='create_category_ajax'),
    path('categories/', views.list_categories, name='list_categories'),

    path('about/', views.about, name='about'),

    path('create/', login_required(views.create_book_view), name='create_book'),

    path('book/detail_book/<str:id>/', views.view_book_detail, name='detail_book'),
    path('book/update/<str:id>/', login_required(views.update_book_view), name='update_book'),
    path('book/delete/<str:id>/', login_required(views.delete_book_view), name='delete_book'),

    path('favourite/', login_required(views.favourite_view), name='favourite'),
    path('book/fav/add/<str:id>/', login_required(views.add_to_favourites), name='addtofav'),
    path('book/fav/remove/<str:id>/', login_required(views.remove_favourite), name='removefav'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
