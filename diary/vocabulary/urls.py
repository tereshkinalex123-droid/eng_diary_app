from django.urls import path
from . import views

urlpatterns = [

    path('', views.deck_list, name='deck_list'),

    path('decks/add/', views.deck_create, name='deck_create'),
    path('decks/<slug:deck_slug>/', views.deck_detail, name='deck_detail'),
    path('decks/<slug:deck_slug>/delete/', views.deck_delete, name='deck_delete'),

    path('words/add/', views.word_create, name='word_create'),
    path('decks/<slug:deck_slug>/words/add/', views.word_create, name='word_create_in_deck'),

    path('words/<slug:word_slug>/', views.word_update, name='word_update'),
    path('words/<slug:word_slug>/delete/', views.word_delete, name='word_delete'),

    path('review/', views.review, name='review_global'),
    path('decks/<slug:deck_slug>/review/', views.review, name='review_deck'),
]