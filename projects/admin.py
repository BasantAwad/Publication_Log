from django.contrib import admin
from .models import Project, Publication, Author
from django.contrib import admin
from .models import MatchRequest

admin.site.register(Project)
admin.site.register(Publication)
admin.site.register(Author)

@admin.register(MatchRequest)
class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ('publication', 'match_title', 'match_score', 'approved', 'created_at')
    list_filter = ('approved',)
    actions = ['approve_match', 'reject_match']

    @admin.action(description="Mark selected matches as approved")
    def approve_match(self, request, queryset):
        queryset.update(approved=True)

    @admin.action(description="Mark selected matches as rejected")
    def reject_match(self, request, queryset):
        queryset.update(approved=False)