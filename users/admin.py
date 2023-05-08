from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

class UsersAdmin(UserAdmin):
    list_display = ('email','username','first_name','last_name','last_login','date_joined','is_active')
    list_display_links =('email','username')
    readonly_fields = ('last_login','date_joined')
    ordering = ('-date_joined',)
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;" >'.format(object.profile_image.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user','city','state','country')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(User, UsersAdmin)