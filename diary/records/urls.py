from django.urls import path
from . import views

urlpatterns = [
    path('', views.record_list, name='record_list'),  # главная страница раздела
    path('add/', views.add_record, name='add_record'),
    path('statistics/', views.show_statistics, name='show_statistics'),
    path('<slug:slug>/', views.show_record, name='show_record'),
    path('<slug:slug>/edit/', views.edit_record, name='edit_record'),
]