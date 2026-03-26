from django.contrib import admin
from .models import Deck, Card, Review

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

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'deck', 'slug', 'front', 'back', 'created_at')
    search_fields = ('front', 'back')
    search_help_text = "Search by front or back of card"
    list_filter = ('user', 'deck',)
    readonly_fields = ('created_at', 'interval', 'repetitions', 'ease_factor', 'next_review', 'last_review')

    @admin.display(description="Interval")
    def interval(self, obj):
        return obj.review.interval if hasattr(obj, 'review') else None
    @admin.display(description="Repetitions")
    def repetitions(self, obj):
        return obj.review.repetitions if hasattr(obj, 'review') else None
    @admin.display(description="Ease_factor")
    def ease_factor(self, obj):
        return obj.review.ease_factor if hasattr(obj, 'review') else None
    @admin.display(description="Next_review")
    def next_review(self, obj):
        return obj.review.next_review if hasattr(obj, 'review') else None
    @admin.display(description="Last_review")
    def last_review(self, obj):
        return obj.review.last_review if hasattr(obj, 'review') else None

    fieldsets = (
    ("Main",  {'fields': ('user', 'deck', 'slug')}),
    ("Content",  {'fields': ('front', 'back', 'examples', 'hint')}),
    ("Review",  {'fields': ('interval', 'repetitions', 'ease_factor', 'next_review', 'last_review')}),
    ("Another",  {'fields': ('created_at',)}),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('card_user', 'card', 'next_review', 'last_review')
    search_fields = ('card__front',)
    search_help_text = "Search by card"
    readonly_fields = ('card_user', 'card')
    @admin.display(description="User")
    def card_user(self, obj):
        return obj.card.user

    fieldsets = (
    ("Main",  {'fields': ('card_user', 'card')}),
    ("Info",  {'fields': ('interval', 'repetitions', 'ease_factor')}),
    ("Review",  {'fields': ('next_review', 'last_review')}),
    )
