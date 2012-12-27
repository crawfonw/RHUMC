from django.contrib import admin

from models import Attendee, Conference

class FengShuiAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_per_page = 50

'''
class MapAdmin(FengShuiAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'game', 'visibility',)
        }),
        ('Share Options', {
            'classes': ('collapse',),
            'fields': ('read_shares', 'write_shares',)
        }),
        ('Associated Objects', {
            'classes': ('collapse',),
            'fields': ('floors',),
        }),
    )
    filter_horizontal = ('read_shares', 'write_shares', 'floors',)
    list_display = ('name', 'owner', 'game', 'visibility',)
    list_filter = ('visibility',)
    search_fields = ('name', 'owner', 'game',)
'''
    
class AttendeeAdmin(FengShuiAdmin):
    list_display = ('owner', 'last_name', 'first_name', 'school', 'attendee_type', 'is_submitting_talk',)

class ConferenceAdmin(FengShuiAdmin):
    filter_horizontal = ('participants',)
    list_display = ('name', 'start_date', 'end_date',)
    search_fields = ('name',)

admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(Conference, ConferenceAdmin)