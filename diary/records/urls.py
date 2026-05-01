from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('', views.record_list, name='record_list'),  #+
    path('add/', views.add_record, name='add_record'),#+
    path('statistics/', views.show_statistics, name='statistics'),#+
    path('create-tag/', views.create_tag, name='create_tag'),#
    path('<slug:slug>/delete/', views.delete_record, name='delete_record'),#
    path('<slug:slug>/edit/', views.edit_record, name='edit_record'),#
    path('<slug:slug>/', views.show_record, name='record'),#
]
