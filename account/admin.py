from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Lawyer, Language


class LawyerInline(admin.StackedInline):
    model = Lawyer

class UserAdmin(BaseUserAdmin):
    inlines = [LawyerInline]


admin.site.register(Language)
admin.site.register(User, UserAdmin)

