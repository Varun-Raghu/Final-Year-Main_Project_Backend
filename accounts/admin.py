from django.contrib import admin
from .models import User, OneTimePassword, Landmark
from django.utils.html import format_html


admin.site.register(OneTimePassword)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['image_tag','phone_number','first_name','last_name','email','id']
    search_fields = ['first_name','last_name','phone_number','email']
    list_filter = ['is_active','is_verified','auth_provider']
    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:30px; max-height:30px; border-radius: 50%; object-fit: cover;"/>'.format(obj.profile_pic))

    image_tag.short_description = 'Profile'

@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    list_display = ['user','landId']
    search_fields = ['user__first_name', 'user__last_name', 'user__phone_number', 'user__email']
    