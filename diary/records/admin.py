from django.contrib import admin
from .models import Record, Tag

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'slug', 'get_tags','word_count' , 'date')
    search_fields = ('title', 'content')
    search_help_text = "Search by title or content"
    list_filter = ('user', 'title', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-date',)

    @admin.display(description='Tags')
    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('tags')

    readonly_fields = ('user', 'date', 'word_count', 'get_tags')

    fieldsets = (
    ("Main",  {'fields': ('user', 'title', 'slug')}),
    ("Content",  {'fields': ('content', 'get_tags', 'word_count')}),
    ("Another",  {'fields': ('date',)})
    )

    @admin.display(description='Word count')
    def word_count(self, obj):
        return f"This entry contains {obj.word_count()} words"

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)