from django.urls import path
from . import views

urlpatterns = [

    path('', views.deck_list, name='deck_list'),

    path('decks/add/', views.deck_create, name='deck_create'),
    path('decks/<slug:deck_slug>/cards/', views.deck_detail, name='deck_detail'),
    path('decks/<slug:deck_slug>/delete/', views.deck_delete, name='deck_delete'),

    path('cards/add/', views.card_create, name='card_create'),
    path('cards/', views.card_list, name='common_deck'),
    path('decks/<slug:deck_slug>/cards/add/', views.card_create, name='card_create_in_deck'),

    path('cards/<slug:card_slug>/', views.card_edit, name='card_edit'),
    path('cards/<slug:card_slug>/delete/', views.card_delete, name='card_delete'),

    path('review/', views.review, name='review_global'),
    path('decks/<slug:deck_slug>/review/', views.review, name='review_deck'),
]