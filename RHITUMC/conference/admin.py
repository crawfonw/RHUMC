from django.contrib import admin

from models import Attendee, Conference, Contactee, Page, Room, Track, Day, TimeSlot, Session, SpecialSession

def pair_for_housing(modeladmin, request, queryset):
    queryset.update(has_been_paired_for_housing=True)
pair_for_housing.short_description = 'Pair for Housing'

def unpair_for_housing(modeladmin, request, queryset):
    queryset.update(has_been_paired_for_housing=False)
unpair_for_housing.short_description = 'Unpair for Housing'

class FengShuiAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_per_page = 50
    
class AttendeeAdmin(FengShuiAdmin):
    #TODO: add "Toggle Room Paired" action
    fieldsets = (
                  ('General Information', {
                          'fields': ('conference', 'first_name', 'last_name', 'email', 'sex',),
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
                                     'fields': ('dietary_restrictions', 'requires_housing', 'has_been_paired_for_housing', 'comments',),
                                     })
                  
                  )
    list_display = ('__unicode__', 'school', 'attendee_type', 'is_submitting_talk', 'requires_housing', 'has_been_paired_for_housing', 'conference',)
    list_filter = ('attendee_type', 'is_submitting_talk', 'requires_housing', 'has_been_paired_for_housing', 'conference',)
    search_fields = ('first_name', 'last_name', 'school', 'paper_title', 'paper_abstract', 'dietary_restrictions', 'comments',)
    actions = (pair_for_housing, unpair_for_housing,)

class PageAdmin(FengShuiAdmin):
    fieldsets = (
                  ('General Settings', {
                                        'fields': ('title',),
                                        }),
                  ('Link Settings', {
                                     'fields': ('is_link', 'link',),
                                    }),
                  ('Page Settings', {
                                    'fields': ('on_sidebar', 'page_text',),
                                    }),
                  )

class ConferenceAdmin(FengShuiAdmin):
    list_display = ('name', 'start_date', 'end_date', 'registration_open', 'past_conference',)
    list_filter = ('registration_open',)
    search_fields = ('name',)
    
class SessionAdmin(FengShuiAdmin):
    filter_horizontal = ('speakers',)
    list_display = ('day', 'time', 'chair',)
    
#class SpecialSessionAdmin(FengShuiAdmin):
    

admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Contactee)
admin.site.register(Day)
admin.site.register(Page, PageAdmin)
admin.site.register(Room)
admin.site.register(Track)
admin.site.register(Session, SessionAdmin)
admin.site.register(SpecialSession)
admin.site.register(TimeSlot)