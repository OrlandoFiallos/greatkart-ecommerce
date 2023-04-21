from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

class UsersAdmin(UserAdmin):
    list_display = ('email','username','first_name','last_name','last_login','date_joined','is_active')
    list_display_links =('email','username')
    readonly_fields = ('last_login','date_joined')
    ordering = ('-date_joined',)
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(User, UsersAdmin)