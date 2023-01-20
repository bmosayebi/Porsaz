from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin	

from . import models

class UserProfileAdmin(ModelAdminJalaliMixin, UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'is_active', 'get_date_joined']

    search_fields = ['username', 'first_name', 'last_name']
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'date_joined', ('first_name', 'last_name'), 'goal','is_active', 'phone_valid', 'register_complete' )}),    )

    ordering = ('-date_joined', 'username', 'first_name', 'last_name', 'is_active',)
    filter_horizontal = ()
    
    def get_date_joined(self, obj):
        return datetime2jalali(obj.date_joined).strftime('%y/%m/%d _ %H:%M:%S')
	
    get_date_joined.short_description = 'زمان ثبت نام'
    get_date_joined.admin_order_field = 'date_joined'


admin.site.register(models.UserProfile, UserProfileAdmin)

admin.site.unregister(Group)