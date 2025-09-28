from django.contrib import admin
from .models import NeetCounsellingSeatAllotmentTracker

@admin.register(NeetCounsellingSeatAllotmentTracker)
class CounsellingSeatAdmin(admin.ModelAdmin):
    list_display = ('seqno', 'name', 'phone_number', 'email', 'rank_no', 'state')
    search_fields = ('name', 'phone_number', 'email', 'rank_no')
