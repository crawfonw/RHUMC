from django.contrib import admin

from models import Attendee, Conference

class FengShuiAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_per_page = 50
    
class AttendeeAdmin(FengShuiAdmin):
    fieldsets = (
                  (None, {
                          'fields': ('owner', 'first_name', 'last_name', ),
                          }),
                  ('School Information', {
                                          'classes': ('collapse',),
                                          'fields': ('school', 'size_of_institute', 'attendee_type', 'year',),
                                          }),
                  ('Talk Information', {
                                        'classes': ('collapse',),
                                        'fields': ('is_submitting_talk', 'paper_title', 'paper_abstract', 'is_submitted_for_best_of_competition',),
                                        }),
                  ('Miscellaneous', {
                                     'classes': ('collapse',),
                                     'fields': ('dietary_restrictions', 'requires_housing', 'comments',),
                                     })
                  
                  )
    list_display = ('owner', 'last_name', 'first_name', 'school', 'attendee_type', 'is_submitting_talk',)
    list_filter = ('owner', 'school', 'attendee_type', 'is_submitting_talk',)

class ConferenceAdmin(FengShuiAdmin):
    filter_horizontal = ('participants',)
    list_display = ('name', 'start_date', 'end_date',)
    search_fields = ('name',)

admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(Conference, ConferenceAdmin)