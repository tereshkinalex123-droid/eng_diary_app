from django.contrib import admin
from .models import Deck, Card

class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    readonly_fields = ('slug', 'front', 'back', 'created_at')
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
