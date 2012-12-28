from django.contrib import admin

from models import Attendee, Conference, Page

class FengShuiAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_per_page = 50
    
class AttendeeAdmin(FengShuiAdmin):
    fieldsets = (
                  (None, {
                          'fields': ('owner', 'conference', 'first_name', 'last_name', 'email', 'sex',),
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
    list_display = ('__unicode__', 'owner', 'school', 'attendee_type', 'is_submitting_talk', 'requires_housing', 'conference',)
    list_filter = ('owner', 'attendee_type', 'is_submitting_talk', 'requires_housing', 'conference',)

class PageAdmin(FengShuiAdmin):
    fieldsets = (
                  (None, {
                          'fields': ('title',),
                          }),
                  ('Link Settings', {
                                          'classes': ('collapse',),
                                          'fields': ('is_link', 'link',),
                                          }),
                  ('Page Settings', {
                                        'classes': ('collapse',),
                                        'fields': ('on_sidebar', 'page_text',),
                                        }),
                  )

class ConferenceAdmin(FengShuiAdmin):
    list_display = ('name', 'start_date', 'end_date',)
    search_fields = ('name',)

admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Page, PageAdmin)