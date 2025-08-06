from django.contrib import admin
from .models import Project, Publication, Author
from django.contrib import admin
from .models import MatchRequest
from django.utils.html import format_html

admin.site.register(Project)
admin.site.register(Publication)
admin.site.register(Author)

@admin.register(MatchRequest)
class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ('publication', 'project', 'match_score', 'approved', 'review_status')

    def review_status(self, obj):
        if obj.approved is None:
            return format_html('<span style="color:orange;">Pending</span>')
        elif obj.approved:
            return format_html('<span style="color:green;">Approved</span>')
        else:
            return format_html('<span style="color:red;">Rejected</span>')
    review_status.short_description = 'Review Status'