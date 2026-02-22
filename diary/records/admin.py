from django.contrib import admin
from .models import Record, Correction, Expression, UserExpressionProgress, Tag

admin.site.register(Record)
admin.site.register(Correction)
admin.site.register(Expression)
admin.site.register(UserExpressionProgress)
admin.site.register(Tag)