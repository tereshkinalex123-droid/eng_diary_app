from django.urls import path
from . import views

app_name = 'vocabulary'

urlpatterns = [

    path('', views.deck_list, name='deck_list'),

    path('decks/add/', views.deck_create, name='deck_create'),
    path('decks/<slug:deck_slug>/cards/', views.deck_detail, name='deck_detail'),
    path('decks/<slug:deck_slug>/delete/', views.deck_delete, name='deck_delete'),

    path('cards/add/', views.card_create, name='card_create'),
    path('cards/', views.card_list, name='common_deck'),
    path('decks/<slug:deck_slug>/cards/add/', views.card_create, name='card_create_in_deck'),

    path('cards/<int:id>/', views.card_edit, name='card_edit'),
    path('cards/<slug:card_slug>/delete/', views.card_delete, name='card_delete'),

    path('start_review/<slug:deck_slug>/', views.start_review_setup, name='review_setup'),
    path('start_common_review/', views.start_review_setup, name='common_review_setup'),
    path('end_review/<int:session_id>/', views.end_review, name='end_review'),
    path('cards/<slug:deck_slug>/review', views.review_card, name='review_card'),
    path('cards/common_review', views.review_card, name='common_review_card'),
    path('cards/review/<int:session_id>/results', views.session_results, name='session_results'),
    path('common_review/confirm/', views.confirm_review, name='confirm_common_review'),
    path('review/<slug:deck_slug>/confirm/', views.confirm_review, name='confirm_review'),
]