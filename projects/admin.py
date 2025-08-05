from django.contrib import admin
from .models import Project, Publication, Author
from django.contrib import admin
from .models import HarvestMatchCandidate

admin.site.register(Project)
admin.site.register(Publication)
admin.site.register(Author)

@admin.register(HarvestMatchCandidate)
class HarvestMatchCandidateAdmin(admin.ModelAdmin):
    list_display = ('publication', 'project', 'confidence_score', 'confirmed_by_admin')
    actions = ['confirm_matches', 'reject_matches']

    def confirm_matches(self, request, queryset):
        updated = queryset.update(confirmed_by_admin=True)
        self.message_user(request, f"{updated} match(es) confirmed.")

    def reject_matches(self, request, queryset):
        updated = queryset.update(confirmed_by_admin=False)
        self.message_user(request, f"{updated} match(es) rejected.")

    confirm_matches.short_description = "Confirm selected matches"
    reject_matches.short_description = "Reject selected matches"