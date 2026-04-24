from django.contrib import admin
from .models import Deck, Card, CardProgress

class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    can_delete = False

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'slug', 'count_cards', 'created_at')
    search_fields = ('name',)
    search_help_text = "Search by deck name"
    list_filter = ('user', 'name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    fieldsets = (
    ("Main",  {'fields': ('user', 'name', 'slug')}),
    ("Another",  {'fields': ('created_at',)}),
    )

    inlines = [CardInline]

    @admin.display(description='cards count')
    def count_cards(self, obj):
        return f"A deck contains {obj.cards.count()} cards"

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'front', 'slug', 'deck', 'created_at')
    search_fields = ('front',)
    search_help_text = "Search by card front"
    list_filter = ('user', 'front', 'deck')
    prepopulated_fields = {'slug': ('front',)}
    readonly_fields = ('created_at',)

@admin.register(CardProgress)
class CardProgressAdmin(admin.ModelAdmin):
    list_display = ('card', 'user', 'next_review', 'repetitions', 'interval')
    list_filter = ('user', 'next_review')
    search_fields = ('card__front', 'user__username')