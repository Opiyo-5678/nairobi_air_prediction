from django.contrib import admin
from .models import CleanAirWarrior, ConsultationRequest, Appointment, Donation

class CleanAirWarriorAdmin(admin.ModelAdmin):
    list_display = ('name', 'expertise', 'email', 'availability')
    search_fields = ('name', 'expertise')
    list_filter = ('expertise',)
    readonly_fields = ('profile_picture_preview',)
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return mark_safe(f'<img src="{obj.profile_picture.url}" style="max-height: 200px; max-width: 200px;" />')
        return "No Image"
    profile_picture_preview.short_description = 'Profile Preview'

class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('warrior', 'name', 'email', 'submitted_at')
    list_filter = ('warrior', 'submitted_at')
    search_fields = ('name', 'email', 'issue')
    date_hierarchy = 'submitted_at'

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('warrior', 'name', 'email', 'date', 'is_confirmed')
    list_filter = ('warrior', 'date', 'is_confirmed')
    search_fields = ('name', 'email', 'reason')
    date_hierarchy = 'date'
    list_editable = ('is_confirmed',)

class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'phone_number', 'status', 'date')
    list_filter = ('status', 'date')
    readonly_fields = ('id', 'date', 'confirmation_date')
    fieldsets = (
        (None, {
            'fields': ('user', 'amount', 'phone_number', 'status')
        }),
        ('MPesa Details', {
            'fields': ('mpesa_receipt',)
        }),
        ('Confirmation', {
            'fields': ('confirmed_by', 'confirmation_date')
        }),
    )

admin.site.register(CleanAirWarrior, CleanAirWarriorAdmin)
admin.site.register(ConsultationRequest, ConsultationRequestAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Donation, DonationAdmin)